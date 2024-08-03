Name:			supernovas
Version:		1.1.0
Release:		2%{?dist}
Summary:		The Naval Observatory's NOVAS C astronomy library, made better 
License:		Unlicense
URL:			https://smithsonian.github.io/SuperNOVAS
Source0:		https://github.com/Smithsonian/SuperNOVAS/archive/refs/tags/v%{version}.tar.gz
BuildRequires:		gcc
BuildRequires:		sed
BuildRequires:		doxygen >= 1.9.0
Suggests:		%{name}-cio-data = %{version}-%{release}
Suggests:		%{name}-solsys1 = %{version}-%{release}
Suggests:		%{name}-solsys2 = %{version}-%{release}

%description

SuperNOVAS is a C/C++ astronomy library, providing high-precision astronomical 
calculations such as one might need for running an observatory or a precise 
planetarium program. It is a fork of the Naval Observatory Vector Astrometry 
Software (NOVAS) C version 3.1, providing bug fixes and making it easier to 
use overall.

The main goals of SuperNOVAS are to improve usability, add new features, 
promote best practices, and provide accessible documentation -- all while 
retaining 100 percent API compatibility with NOVAS C 3.1. Thus, if you have 
written code for NOVAS C 3.1, you can build it with SuperNOVAS also.

SuperNOVAS is entirely free to use without licensing restrictions. Its source 
code is compatible with the C90 standard, and hence should be suitable for old 
and new platforms alike. It is light-weight and easy to use, with full support 
for the IAU 2000/2006 standards for sub-micro-arc-second position 
calculations.

%package solsys1
Summary: Legacy solar-system plugin for JPL DE200 through DE421
Requires:		%{name}%{_isa} = %{version}-%{release}

%description solsys1
Optional SuoperNOVAS plugin library that provides legacy solar-system routines 
for accessing older JPL planetary data (DE200 through DE421).
 
%package solsys2
Summary: Legacy solar-system plugin for the JPL PLEPH routines
Requires:		%{name}%{_isa} = %{version}-%{release}

%description solsys2
Optional SuperNOVAS plugin library that provides legacy solar-system routines 
for accessing older JPL planetary data through the JPL PLEPH routines. It 
requires a user-provided FORTRAN adapter module, and PLEPH library. This 
package is provided only to support legacy applications that were written for 
that particular interfacing.

%package cio-data
Summary:		CIO location data for the SuperNOVAS C/C++ astronomy library
BuildArch:		noarch

%description cio-data
Optional CIO location vs GCRS lookup table. This file is not normally required
for the operation of the library. It is needed only if the user explicitly needs
to know the location of the CIO vs GCRS, rather than w.r.t. the equinox of date.
Applications that require CIO location w.r.t. the GCRS should depend on this
sub-package

%package devel
Summary:		C development files for the SuperNOVAS C/C++ astronomy library
Requires:		%{name}%{_isa} = %{version}-%{release}
Requires:		%{name}-solsys1%{_isa} = %{version}-%{release}
Requires:		%{name}-solsys2%{_isa} = %{version}-%{release}

%description devel
This sub-package provides C headers and non-versioned shared library symbolic 
links for the SuperNOVAS C/C++ library. It also provides a default FORTRAN
adapter module (as documentation) that may be used as is, or modified as 
needed, for the the JPL PLEPH module.


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

make %{?_smp_mflags} distro CIO_LOCATOR_FILE=%{_datadir}/%{name}/CIO_RA.TXT

%check

make test

%install

# ----------------------------------------------------------------------------
# Install libsupernovas.so.1 runtime library
mkdir -p %{buildroot}/%{_libdir}

# ----------------------------------------------------------------------------
# libsupernovas.so...
install -m 755 lib/lib%{name}.so.1 %{buildroot}/%{_libdir}/lib%{name}.so.%{version}

# Link libsopernovas.so.1.x.x -> libsupernovas.so.1
( cd %{buildroot}/%{_libdir} ; ln -sf lib%{name}.so.{%version} lib%{name}.so.1 )

# Link libsupernovas.so.1 -> libsupernovas.so
( cd %{buildroot}/%{_libdir} ; ln -sf lib%{name}.so.1 lib%{name}.so )

# ----------------------------------------------------------------------------
# libsolsys1.so
install -m 755 lib/libsolsys1.so.1 %{buildroot}/%{_libdir}/libsolsys1.so.%{version}

# Link libsolsys1.so.1.x.x -> libsols dys1.so.1
( cd %{buildroot}/%{_libdir} ; ln -sf libsolsys1.so.{%version} libsolsys1.so.1 )

# Link libsolsys1.so.1 -> libsolsys1.so
( cd %{buildroot}/%{_libdir} ; ln -sf libsolsys1.so.1 libsolsys1.so )

# ----------------------------------------------------------------------------
# libsolsys2.so
install -m 755 lib/libsolsys2.so.1 %{buildroot}/%{_libdir}/libsolsys2.so.%{version}

# Link libsolsys2.so.1.x.x -> libsolsys2.so.1
( cd %{buildroot}/%{_libdir} ; ln -sf libsolsys2.so.{%version} libsolsys2.so.1 )

# Link libsolsys2.so.1 -> libsolsys2.so
( cd %{buildroot}/%{_libdir} ; ln -sf libsolsys2.so.1 libsolsys2.so )

# ----------------------------------------------------------------------------
# Install runtime CIO locator data 
mkdir -p %{buildroot}/%{_datadir}/%{name}
install -m 644 data/CIO_RA.TXT %{buildroot}/%{_datadir}/%{name}/CIO_RA.TXT

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
install -m 644 apidoc/supernovas.tag %{buildroot}/%{_docdir}/%{name}/%{name}.tag

# ----------------------------------------------------------------------------
# examples
install -m 644 -D examples/* %{buildroot}/%{_docdir}/%{name}/


%files
%license LICENSE
%doc CHANGELOG.md
%{_libdir}/lib%{name}.so.1{,.*}

%files solsys1
%{_libdir}/libsolsys1.so.1{,.*}

%files solsys2
%{_libdir}/libsolsys2.so.1{,.*}

%files cio-data
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/CIO_RA.TXT

%files devel
%doc README-orig.md CONTRIBUTING.md
%doc %{_docdir}/%{name}/example.c
%doc %{_docdir}/%{name}/example-usno.txt
%doc %{_docdir}/%{name}/jplint.f
%{_prefix}/include/*
%{_libdir}/*.so

%files doc
%doc %{_docdir}/%{name}/%{name}.tag
%doc %{_docdir}/%{name}/html


%changelog
%autochangelog

