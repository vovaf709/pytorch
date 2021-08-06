From its inception, PyTorch has strived to be broadly compatible with
wide ranges of upstream tools and libraries. We take a pragmatic
approach to what we support based on what our users commonly use. We
can't reasonably support everything, but we do follow some principles
that inform what we do support.

This document does not enumerate in detail every upstream package
version that is supported, but instead focuses on some of the more
important principles that can in general be extrapolated to upstream
packages at large.

Upstream packages that are discussed here:
- Python
- Compilers
  - GCC
  - Clang
  - Visual C++

Python
======
Our Python story is simple. We support the Python releases that are
actively supported by the Python Software Foundation, possibly with
some delay for very new releases.

As of 6/Aug/2021, this list is:
- Python 3.9
- Python 3.8
- Python 3.7
- Python 3.6

### Upcoming changes
Python 3.10 is scheduled for release 04/Oct/2021.  
Support for Python 3.6 ends 23/Dec/2021.

[Python releases](https://www.python.org/downloads/)

Compilers
=========
PyTorch contains much C++ code and we actively support three of the
most common compilers:
- GCC
- Clang
- Visual C++

We have different criteria for how we decide the minimally supported
version of each compiler.

### Visual C++
The story for Visual C++ is simple: we support the oldest version that
Microsoft supports. As of 6/Aug/2021 this is 16.4.

[Visual C++ 2019 releases](https://docs.microsoft.com/en-us/visualstudio/releases/2019/servicing)

### GCC
Many of our users come from Ubuntu, which provides long-term support
(LTS) versions of its operating system.

We support the oldest version of default GCC that is in a supported
version of Ubuntu. Note that we choose Ubuntu's "end of standard
support" rather than "end of life" to make this decision, as "end of
life" is a very long time and only getting security updates.

This yields GCC 7.5 from Ubuntu 18.04.

### Clang

Similar to GCC, we also use the oldest supported version of Ubuntu to
inform the oldest version of Clang that we support. However, we also
look at the oldest version of macOS, since it ships with Clang via
Xcode. Nevertheless, the version of Clang will be determined by the
Ubuntu version for the foreseeable future since the macOS Xcode
version is much closer to the bleeding edge.

This yields Clang 6.0 from Ubuntu 18.04.

#### Upcoming changes

Visual C++ 16.4 goes out of support in Oct/2021 and then Visual C++
16.7 becomes the oldest version until Apr/2022.

Ubuntu 18.04 will be supported until Apr/2023, so unless we change our
policy, there will be no changes to GCC or Clang until then.

[Ubuntu releases](https://wiki.ubuntu.com/Releases)
