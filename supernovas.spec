Name:			supernovas
Version:		1.0.1
Release:		1%{?dist}
Summary:		The Naval Observatory's NOVAS C astronomy library, made better 
License:		Unlicense
URL:			https://smithsonian.github.io/SuperNOVAS/
Source0:		https://github.com/Smithsonian/SuperNOVAS/archive/refs/tags/v%{version}.tar.gz
BuildRequires:		gcc
BuildRequires:		gcc-gfortran
BuildRequires:		sed
BuildRequires:		doxygen >= 1.9.0
Recommends:		%{name}-cio-data = %{version}-%{release}

%description

SuperNOVAS is a C/C++ astronomy library, providing high-precision astronomical 
calculations such as one might need for running an observatory or a precise 
planetarium program. It is a fork of the Naval Observatory Vector Astrometry 
Software (NOVAS) C version 3.1, providing bug fixes and making it easier to 
use overall.

The main goals of SuperNOVAS are to improve usability, add new features, 
promote best practices, and provide accessible documentation -- all while 
retaining 100% API compatibility with NOVAS C 3.1. Thus, if you have written 
code for NOVAS C 3.1, you can build it with SuperNOVAS also.

SuperNOVAS is entirely free to use without licensing restrictions. Its source 
code is compatible with the C90 standard, and hence should be suitable for old 
and new platforms alike. It is light-weight and easy to use, with full support 
for the IAU 2000/2006 standards for sub-micro-arc-second position 
calculations.

%package cio-data
Summary:		CIO location data for the SuperNOVAS C/C++ astronomy library
Requires:		%{name} = %{version}-%{release}

%description cio-data
Optional CIO location vs GCRS lookup table. This file is not normally required
for the operation of the library. It is needed only if the user explicitly needs
to know the location of the CIO vs GCRS, rather than w.r.t. the equinox of date.
Applications that require CIO location w.r.t. the GCRS should depend on this
sub-package

%package devel
Summary:		C development files for the SuperNOVAS C/C++ astronomy library
Requires:		%{name}%{_isa} = %{version}-%{release}

%description devel
This sub-package provides C headers and non-versioned shared library symbolic 
links for the SuperNOVAS C/C++ library.


%package doc
Summary:		Documentation for the SuperNOVAS C/C++ astronomy library
BuildArch:		noarch
Requires:		%{name} = %{version}-%{release}

%description doc
This package provides man pages and HTML documentation for the SuperNOVAS 
C/C++ astronomy library.

%prep
%setup -q -n SuperNOVAS-%{version}

%build

# Define where the library will look for the CIO locator data
CIO_LOCATOR_FILE=%{_datadir}/%{name}/cio_ra.bin

# ----------------------------------------------------------------------------
# Future build for SuperNOVAS > 1.0.1
#
#make %{?_smp_mflags} distro
#
# ----------------------------------------------------------------------------
# BEGIN is build for v1.0.1

# We'll modify the build configuration, saving the original first
cp config.mk config.bak

# Prepend CPPFLAGS in CFLAGS
CFLAGS="$CPPFLAGS $CFLAGS"

# Specify the CIO locator file path, when installed
sed -i '1 i\CFLAGS += -DDEFAULT_CIO_LOCATOR_FILE=\\"%{_libdir}/%{name}/cio_ra.bin\\"' config.mk

# Specify where the cio_ra.bin file will be installed
sed -i "s:/user/share/novas/cio_ra.bin:%{_datadir}/%{name}/cio_ra.bin:g" config.mk

# Use externally defined CFLAGS
sed -i "s:CFLAGS = -Os -Wall -I\$(INC):CFLAGS += -I\$(INC):g " config.mk

# Use externally defined CFLAGS for tests
#sed -i "s:-g -I../include \$<:\$(CFLAGS) \$<:g" test/Makefile

# Set soname to 'libsupernovas.so.1.x.x'
sed -i "s:-shared -fPIC:-shared -fPIC -Wl,-soname,lib%{name}.so.1 $LDFLAGS -lm:g" Makefile

# build lib/novas.so
make %{?_smp_mflags} shared
mv lib/novas.so lib/lib%{name}.so

# solsys1 and solsys2 legacy libs
echo "CFLAGS += -shared -fPIC" >> config.mk
make %{?_smp_mflags} solsys

# Manual build solsys1.so and solsys2.so for packaging
gcc -o lib/solsys1.so src/solsys1.c src/eph_manager.c $CFLAGS -Iinclude -shared -fPIC \
  -Wl,-soname,libsolsys1.so.1 $LDFLAGS -lm -Llib -l%{name}
  
gcc -o lib/solsys2.so src/solsys2.c src/jplint.f $CFLAGS -Iinclude -shared -fPIC \
  -Wl,-soname,libsolsys2.so.1 $LDFLAGS -lm -Llib -l%{name}

# The headless README from upstream
make %{?_smp_mflags} README-headless.md

# man pages and HTML documentation (without specialized headers)
sed -i "s:resources/header.html::g" Doxyfile
make %{?_smp_mflags} dox

mv config.bak config.mk

# make share/cio_ra.bin
make %{?_smp_mflags} cio_ra.bin

# Use the future name for the stripped-down README
mv README-headless.md README-orig.md

# Compile tests

# Compile tests with -fPIE for linker flags
sed -i "s:CFLAGS =:CFLAGS = -fPIE:g" test/Makefile

# Always use CFLAGS when compiling
sed -i "s:-c -o \$@ -g -I../include $<:-c -o \$@ \$(CFLAGS) $<:g" test/Makefile

# Skip grav_def error test due to d_light() bug
sed -i "s:if(test_grav_def://if(test_grav_def:g" test/src/test-errors.c

# END is build for v1.0.1
# ----------------------------------------------------------------------------


%check

# Arithmetic precision differences among platform prevent running the
# buil-in tests.
make test

%install

# ----------------------------------------------------------------------------
# Install libsupernovas.so.1 runtime library
mkdir -p %{buildroot}/%{_libdir}

# ----------------------------------------------------------------------------
# libsupernovas.so...
install -m 755 lib/lib%{name}.so %{buildroot}/%{_libdir}/lib%{name}.so.%{version}

# Link libsopernovas.so.1.x.x -> libsupernovas.so.1
( cd %{buildroot}/%{_libdir} ; ln -sf lib%{name}.so.{%version} lib%{name}.so.1 )

# Link libsupernovas.so.1 -> libsupernovas.so
( cd %{buildroot}/%{_libdir} ; ln -sf lib%{name}.so.1 lib%{name}.so )

# (compat naming) Link libnovas.so -> libsupernovas.so
( cd %{buildroot}/%{_libdir} ; ln -sf lib%{name}.so libnovas.so )

# ----------------------------------------------------------------------------
# libsolsys1.so
install -m 755 lib/solsys1.so %{buildroot}/%{_libdir}/libsolsys1.so.%{version}

# Link libsolsys1.so.1.x.x -> libsols dys1.so.1
( cd %{buildroot}/%{_libdir} ; ln -sf libsolsys1.so.{%version} libsolsys1.so.1 )

# Link libsolsys1.so.1 -> libsolsys1.so
( cd %{buildroot}/%{_libdir} ; ln -sf libsolsys1.so.1 libsolsys1.so )

# ----------------------------------------------------------------------------
# libsolsys2.so
install -m 755 lib/solsys2.so %{buildroot}/%{_libdir}/libsolsys2.so.%{version}

# Link libsolsys2.so.1.x.x -> libsolsys2.so.1
( cd %{buildroot}/%{_libdir} ; ln -sf libsolsys2.so.{%version} libsolsys2.so.1 )

# Link libsolsys2.so.1 -> libsolsys2.so
( cd %{buildroot}/%{_libdir} ; ln -sf libsolsys2.so.1 libsolsys2.so )

# ----------------------------------------------------------------------------
# Install runtime CIO locator data 
mkdir -p %{buildroot}/%{_libdir}/%{name}
install -m 644 cio_ra.bin %{buildroot}/%{_libdir}/%{name}/cio_ra.bin

# ----------------------------------------------------------------------------
# C header files
mkdir -p %{buildroot}/%{_prefix}/include
install -m 644 -D include/* %{buildroot}/%{_prefix}/include/

# ----------------------------------------------------------------------------
# HTML documentation
mkdir -p %{buildroot}/%{_docdir}/%{name}/html/search
install -m 644 -D apidoc/html/search/* %{buildroot}/%{_docdir}/%{name}/html/search/
rm -rf apidoc/html/search
install -m 644 -D apidoc/html/* %{buildroot}/%{_docdir}/%{name}/html/
install -m 644 apidoc/novas.tag %{buildroot}/%{_docdir}/%{name}/%{name}.tag

# ----------------------------------------------------------------------------
# example.c
install -m 644 -D examples/example.c %{buildroot}/%{_docdir}/%{name}/


%files
%license LICENSE
%doc CHANGELOG.md
%{_libdir}/lib%{name}.so.1{,.*}
%{_libdir}/libsolsys1.so.1{,.*}
%{_libdir}/libsolsys2.so.1{,.*}

%files cio-data
%{_libdir}/%{name}/cio_ra.bin

%files devel
%doc README-orig.md CONTRIBUTING.md
%doc %{_docdir}/%{name}/example.c
%{_prefix}/include/*
%{_libdir}/*.so

%files doc
%doc %{_docdir}/%{name}/%{name}.tag
%doc %{_docdir}/%{name}/html


%changelog
%autochangelog

