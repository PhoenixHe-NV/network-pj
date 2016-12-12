import gzip
import socket
import unittest
import subprocess
import tempfile
import sys
import io
import urllib.request

test_cmd = "curl --verbose --silent -m 5 --compress --max-redirs 0 -H 'Accept-Encoding: gzip'"
# test_cmd = "java -jar labget.jar"
test_cmd = test_cmd.split(" ")

# Change this to False if you doesn't want to support ipv6
support_ipv6 = True
# Change this to False if you doesn't want to support https
support_https = True

support_ipv6 = support_ipv6 and socket.has_ipv6


def test_get(command, url, extra_func=None, timeout=16, query=""):
    stdout_file = tempfile.TemporaryFile()
    stderr_file = tempfile.TemporaryFile()
    if query:
        url = url + '?' + query

    try:
        child = subprocess.Popen(command + [url], stdout=stdout_file, stderr=stderr_file)

        if extra_func is not None:
            extra_func()

        exit_code = child.wait(timeout)
        stdout_file.seek(0)
        stderr_file.seek(0)
        stdout = stdout_file.read()
        stderr = stderr_file.read()
        print("Call", " ".join(command), url, ", return", exit_code,
              ", stdout size:", len(stdout), ", stderr size:", len(stderr), file=sys.stderr)

        return stdout, stderr, exit_code

    finally:
        stdout_file.close()
        stderr_file.close()


opener = urllib.request.build_opener()
opener.addheaders = []


def py_get(url, query):
    if query:
        url = url + '?' + urllib.parse.urlencode(query)
    try:
        req = urllib.request.Request(url)
        rsp = opener.open(req, timeout=5)
        data, code = rsp.read(), rsp.getcode()
        if rsp.info().get('Content-Encoding') == 'gzip':
            buf = io.BytesIO(data)
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        return data, code

    except urllib.request.HTTPError as e:
        return e.read(), e.code


def test_fetch_content(self, url, simple_check=False, query=""):
    std = dict()
    test = dict()

    def func():
        std["data"], std["code"] = py_get(url, query=query)

    test["data"], test["stderr"], test["exit_code"] = test_get(test_cmd, url, func, query=query)
    self.assertEqual(test["exit_code"], 0, "Exit code of your program is not 0")
    if simple_check:
        self.assertEqual(len(std["data"]), len(test["data"]),
                         "Data fetched from your program is not correct")
    else:
        self.assertEqual(std["data"], test["data"],
                         "Data fetched from your program is not correct")
    self.assertTrue(test["stderr"].find(bytes(str(std["code"]), "utf-8")) >= 0,
                    "Expect HTTP response startline with code " + str(std["code"]) +
                    " in stderr")
    return std, test


def test_resolve(self, host, family=socket.AF_INET):
    result = dict()

    def func():
        _, _, _, _, endpoint = socket.getaddrinfo(host, None, family)[0]
        result['ipaddr'] = endpoint[0]

    _, stderr, _ = test_get(test_cmd, "http://" + host, extra_func=func, timeout=6)
    self.assertTrue(stderr.find(bytes(result["ipaddr"], 'utf-8')) >= 0,
                    "Expect resolved address " + result["ipaddr"] + " in stderr")


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        sys.stderr.write("\n")

    def test_dns_resolve(self):
        test_resolve(self, "pj-test-dns.htcnet.moe")

    def test_dns_resolve_not_exist(self):
        host = "no-such-domain.htcnet.moe"
        with self.assertRaises(socket.gaierror):
            socket.getaddrinfo(host, None, socket.AF_INET)

        _, _, exit_code = test_get(test_cmd, "http://" + host, timeout=6)
        self.assertEqual(exit_code, 0, "Should exit 0 if name not resolved.")

    @unittest.skipIf(not support_ipv6, "IPV6 is not supported")
    def test_dns_resolve_v6(self):
        test_resolve(self, "pj-test-dns-v6-only.htcnet.moe", socket.AF_INET6)
        test_resolve(self, "pj-test-dns-v4-v6.htcnet.moe", socket.AF_INET6)

    def test_basic_http(self):
        _, test = test_fetch_content(self, "http://www.fudan.edu.cn/2016/index.html")
        self.assertTrue(test["stderr"].find(b"GET /2016/index.html HTTP/1.1") >= 0,
                        "Expect HTTP request startline in stderr")
        self.assertTrue(test["stderr"].find(b"HTTP/1.1 200 OK") >= 0,
                        "Expect HTTP response startline in stderr")

        _, test = test_fetch_content(self, "http://www.xiami.com", simple_check=True)
        self.assertTrue(test["stderr"].find(b"GET / HTTP/1.1") >= 0,
                        "Expect HTTP startline in stderr")
        self.assertTrue(test["stderr"].find(b"HTTP/1.1 200 OK") >= 0,
                        "Expect HTTP response startline in stderr")

    def test_http_with_port(self):
        test_fetch_content(self, "http://www.urp.fudan.edu.cn:92/eams/login.action",
                           simple_check=True)

    @unittest.skip("Invalid test")
    def test_url_parsing_sp(self):
        test_fetch_content(self, "http://pj-test.htcnet.moe:8033/test_url_parsing",
                           query="?data1=}don'tforgeturlencode{&data2=345%")

    def test_broken_response(self):
        def test_exit_0(url):
            stdout, _, exit_code = test_get(test_cmd, url)
            self.assertEqual(exit_code, 0, "Exit code of your program is not 0")
            self.assertEqual(len(stdout), 0, "stdout should be empty if the response is broken")

        test_exit_0("http://pj-test.htcnet.moe:8031/test/0")
        test_exit_0("http://pj-test.htcnet.moe:8031/test/1")
        test_exit_0("http://pj-test.htcnet.moe:8031/test/2")
        test_exit_0("http://pj-test.htcnet.moe:8031/test/3")
        test_exit_0("http://pj-test.htcnet.moe:8031/test/4")
        test_exit_0("http://pj-test.htcnet.moe:8031/test/5")
        test_exit_0("http://pj-test.htcnet.moe:8031/test/6")
        test_exit_0("http://pj-test.htcnet.moe:8031/test/7")
        # Chunked transfer encoding
        test_exit_0("http://pj-test.htcnet.moe:8031/test/8")

    def test_delayed_response(self):
        test_fetch_content(self, "http://pj-test.htcnet.moe:8032/test/10")
        test_fetch_content(self, "http://pj-test.htcnet.moe:8032/test/11")
        test_fetch_content(self, "http://pj-test.htcnet.moe:8032/test/12")

    @unittest.skipIf(not support_https, "HTTPS is not supported")
    def test_simple_https(self):
        test_fetch_content(self, "https://mirrors.tuna.tsinghua.edu.cn", )
        test_fetch_content(self, "https://mirrors.tuna.tsinghua.edu.cn/centos/RPM-GPG-KEY-CentOS-7")

    @unittest.skipIf(not support_https, "HTTPS is not supported")
    def test_https_with_invalid_cert(self):
        url = "https://kyfw.12306.cn/otn/"
        # Expect certificate validation error on 12306.cn
        with self.assertRaises(urllib.error.URLError):
            py_get(url)
        stdout, stderr, exit_code = test_get(test_cmd, url)
        self.assertNotEqual(exit_code, 0, "Should still return 0 if SSL certificate is invalid")
        self.assertEqual(stdout, b"", "Should not output content if SSL certificate is invalid")

    @unittest.skipIf(not support_ipv6, "IPV6 is not supported")
    def test_ipv6(self):
        test_fetch_content(self, "http://ftp6.sjtu.edu.cn")
        test_fetch_content(self, "http://ftp6.sjtu.edu.cn/centos/RPM-GPG-KEY-CentOS-7")

    @unittest.skipIf(not support_https, "HTTPS is not supported")
    @unittest.skipIf(not support_ipv6, "IPV6 is not supported")
    def test_ipv6_https(self):
        test_fetch_content(self, "https://mirrors6.tuna.tsinghua.edu.cn")
        test_fetch_content(self, "https://mirrors6.tuna.tsinghua.edu.cn/centos/RPM-GPG-KEY-CentOS-7")

    @unittest.skipIf(not support_ipv6, "IPV6 is not supported")
    def test_ipv4_ipv6(self):
        # This site has both A/AAAA record, but v6 address is unreachable.
        # Should fallback to v4
        test_fetch_content(self, "http://pj-test-dns-v4-v6-invalid.htcnet.moe/test")

    def test_chunked_coding(self):
        test_fetch_content(self, "http://pj-test.htcnet.moe:8033/test/20")

    def test_gzip_coding(self):
        _, test = test_fetch_content(self, "http://pj-test.htcnet.moe:8033/test/21")
        self.assertTrue(test["stderr"].find(b"Content-Encoding: gzip") >= 0,
                        "Gzip coding not supported.")
        test_fetch_content(self, "http://pj-test.htcnet.moe:8033/test/22")

    def test_basic_redirect(self):
        pass

    def test_cross_site_redirect(self):
        pass

    def test_redirect_with_cookie(self):
        pass

    @unittest.skipIf(not support_https, "HTTPS is not supported")
    def test_https_redirect(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
