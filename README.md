#Network PJ: DNS query and HTTP request

[TOC]

## Introduction

In this lab, you should implement a simple tool that can download content from the web using http. This tool should:

1. Send __DNS__ query to the __DNS__ server, and get the resolved IP address
2. Send __HTTP__ request to the __HTTP__ server, and bring the result to __stdout__.

Each phrase has basic and extra parts. You **MUST** implement all the basic parts. For the extra parts, you can try some of them. You will get full credit for the lab if you achieve hightest points in the class. You will get 60% of the credit for the lab if you implement all the basic parts correctly.

Please fetch the document from

```
ftp://10.132.141.33/classes/14/161 计算机网络/PROJECT
```

or

```
https://github.com/htc550605125/network-pj
```

You can use **any program language** in this lab on __Windows__ or __OSX__ or __Linux__, but you **should not use any library** for __DNS__ or __HTTP__ if not specifically indicated. You should implement them with your code only.

**You should provide all of your souce code and a document describing how to build and run your program. Please also provide the platform you are using, and what you have implemented, in the document.**

Generally, your program should be named **labget** and accept one argument, the URL:

```shell
> labget http://www.zhihu.com
```

If you want to use java, please provide(build) jar, maven is suggested:

```shell
> java -jar labget.jar http://www.zhihu.com
```



**WARNING! PlAGIARSIM IS NOT ALLOWED OR YOU WILL GET ZERO CREDIT FOR THIS LAB GUARANTEED. DO NOT SHARE ANY CODE WITH YOUR CLASSMATE.**



## Expected Output

If there is no error, your program should send the result to __stdout__. You can print your log to __stderr__. Please at least include the __resolved IP address and HTTP request/response header__ in __stderr__. The exit code of your program should always be 0.

If anything goes wrong, just leave __stdout__ empty and send error message to __stderr__. Please set timeout to **5 seconds** for each network operation.



## RFC Documents

Everything you need to know about the __DNS__ protocol and __HTTP__ protocol is defined in RFC. **Request for Comments** (**RFC**) is a type of publication from the __Internet Engineering Task Force (IETF)__ and the __Internet Society (ISOC)__, the principal technical development and standards-setting bodies for the Internet. They are your friends in this lab. Although they all seem to be very long, you only need a little part of it. Be patient and find out the part you need in RFC while reading.

In this lab, we will touch two protocols: __DNS__ and __HTTP__. For __DNS__ part, you need [RFC 1035](https://tools.ietf.org/html/rfc1035) . For __HTTP__ part, you need [RFC 7230](https://tools.ietf.org/html/rfc7230) .



## Phrase 1: URL parsing 

The HTTP URL scheme is defined in [RFC 7230 Section 2.7](https://tools.ietf.org/html/rfc7230#page-16) . If your program cannot parse the given URL, just print out the error message to __stderr__ and exit.

Hint: use regex for parsing.

In this part, your program __MUST__ support:

1. (5 points) Handle URL path correctly.
2. (5 points) __HTTP__ with default port (80) or custom port.

__Extra__:

1. (5 - 20 points) __HTTPS__ scheme. You can use __TLS__ library for this part, but you can get a big bouns if you implement __TLS__ yourself. And, if you can, try to implement the server certificate validation.


Hint: Use regex for parsing. Read RFC carefully for URL scheme defination.


## Phrase 2: DNS query

Everything is defined in RFC 1035 and RFC 3596(for ipv6). If you are confusing about the RFC document, see an example [here](https://github.com/shadowsocks/shadowsocks/blob/master/shadowsocks/asyncdns.py) . Please send dns query to 202.120.224.26.

In this part, your program __MUST__ support:

1. (30 points) __DNS__ query for ipv4 address (A NAME). Please use custom udp socket. If you have difficulty implementing this part, you can use the system dns resolver, but you will not get full points for this part.

__Extra__:

1. (5 - 20 points) ipv6 support (AAAA NAME). If you want to support ipv6, please try ipv4/ipv6 simultaneously and return the first successful result. Note that there are several conditions: the site doesn't have AAAA record; the site has a AAAA record but cannot connect to the site with ipv6; the running environment doesn't support ipv6.


Note: Almost all the Fudan wireless have ipv6 access. Your dorm's wired port with static ip also have ipv6 access.


## Phrase 3: HTTP request

See RFC 7230. Please send request/response __startline__ and __headers__ to __stderr__. 

In this part, your program __MUST__ support:

1. (10 points) __HTTP 1.1 GET__ request
2. (10 points)  __HTTP 1.1__ response parsing

__Extra__:

1. (5 points) __HTTP 1.1 GET__ with appropriate headers. If you don't know what is appropriate for a HTTP request, see what chrome sends, and read RFC.
2. (10 - 15 points) Follow __HTTP Redirect__ (301, 302). Handle cookie while redirecting.
3. (5 points) Handle chunked transfer coding. See [section 4.1 in RFC 7230](https://tools.ietf.org/html/rfc7230#page-36) .
4. (10 points) Handle gzip coding. See [section 4.2.3 in RFC 7230](https://tools.ietf.org/html/rfc7230#page-39).You can use library for this part.
5. (10 points) Multi-thread downloading with range header. You can detect the total length of the content, if it is bigger then 10M, use multi-thread download to save the content to a temp file, then output the file to __stdout__.

Note: Read the RFC carefully! The behaviour of your code will be concerned on grading.



## Auto Testing

This lab provides a python script for testing. It covers some of the functions above. However, the points you get is not only based on this test.

To run the test, install python3, modify ``test.py`` line 8 to the command that launchs your program. Then, run the script using ``python test.py``. Your program are not required to pass all the test cases. If you want to skip some of the test cases, add

```python
@unittest.skip("Not implemented")
```

before the test function.



## Submit

Compress all of your code and documents into a **zip** file named by your student ID. Upload the zip file to

```
ftp://10.132.141.33/classes/14/161 计算机网络/WORK_UPLOAD/PJ1
```

before 2017/1/1 23:59:59.

If you have any question for this lab, feel free to contact me via

* Wechat: htc550605125
* QQ: 550605125
* Telegram: +86 15221920753  
* Email: 13302010023@fudan.edu.cn