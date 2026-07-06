Name:           modsecurity
Version:        3.0.16
Release:        1%{?dist}
Summary:        ModSecurity v3 library installed under /opt/modsecurity

License:        Apache-2.0
URL:            https://github.com/owasp-modsecurity/ModSecurity
Source0:        v%{version}.tar.gz

%global modsec_prefix /opt/modsecurity

%if 0%{?rhel} == 7
BuildRequires:  devtoolset-11-gcc
BuildRequires:  devtoolset-11-gcc-c++
BuildRequires:  devtoolset-11-libstdc++-devel
BuildRequires:  pkgconfig
Requires:       devtoolset-11-libstdc++-devel
%else
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  pkgconf-pkg-config
%endif

BuildRequires:  make
BuildRequires:  git
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  pcre2-devel
BuildRequires:  libxml2-devel
BuildRequires:  yajl-devel
BuildRequires:  curl-devel
BuildRequires:  lmdb-devel
BuildRequires:  zlib-devel

Requires:       pcre2
Requires:       libxml2
Requires:       yajl
Requires:       libcurl
Requires:       lmdb-libs
Requires:       zlib

Provides:       libmodsecurity = %{version}-%{release}
Provides:       libmodsecurity%{?_isa} = %{version}-%{release}
Provides:       libmodsecurity-devel = %{version}-%{release}
Provides:       libmodsecurity-devel%{?_isa} = %{version}-%{release}
Provides:       modsecurity-devel = %{version}-%{release}
Provides:       modsecurity-devel%{?_isa} = %{version}-%{release}

%description
ModSecurity v3 library installed under /opt/modsecurity.

This package intentionally includes runtime libraries, headers,
pkg-config files, development files, and example configuration files
in a single RPM for local nginx builds.

The Source0 archive must be created from a git checkout after fetching
submodules. Do not use the small GitHub-generated v%{version}.tar.gz
archive directly.

%prep
%autosetup -n ModSecurity-%{version}

test -d others/mbedtls || {
    echo "ERROR: others/mbedtls is missing."
    echo "Create v%{version}.tar.gz from git clone + git submodule update."
    exit 1
}

test -d others/libinjection || {
    echo "ERROR: others/libinjection is missing."
    echo "Create v%{version}.tar.gz from git clone + git submodule update."
    exit 1
}

test -f modsecurity.conf-recommended || {
    echo "ERROR: modsecurity.conf-recommended is missing."
    echo "Create v%{version}.tar.gz from a complete ModSecurity source tree."
    exit 1
}

test -f unicode.mapping || {
    echo "ERROR: unicode.mapping is missing."
    echo "Create v%{version}.tar.gz from a complete ModSecurity source tree."
    exit 1
}

%build
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-11/enable
export CC=gcc
export CXX=g++
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags} -std=gnu++17"
export LDFLAGS="${LDFLAGS:-} -Wl,-rpath,/opt/rh/devtoolset-11/root/usr/lib64"
%endif

./build.sh

%configure \
    --prefix=%{modsec_prefix} \
    --exec-prefix=%{modsec_prefix} \
    --bindir=%{modsec_prefix}/bin \
    --sbindir=%{modsec_prefix}/sbin \
    --includedir=%{modsec_prefix}/include \
    --libdir=%{modsec_prefix}/lib64 \
    --datadir=%{modsec_prefix}/share

make %{?_smp_mflags}

%install
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-11/enable
%endif

rm -rf %{buildroot}

make install DESTDIR=%{buildroot}

mkdir -p %{buildroot}%{modsec_prefix}/include
mkdir -p %{buildroot}%{modsec_prefix}/lib64
mkdir -p %{buildroot}%{modsec_prefix}/lib64/pkgconfig
mkdir -p %{buildroot}%{modsec_prefix}/share

# Install example configuration files under /opt/modsecurity/share.
# These files are not installed under /etc/nginx/modsec.
install -m 0644 modsecurity.conf-recommended \
    %{buildroot}%{modsec_prefix}/share/modsecurity.conf-recommended

install -m 0644 unicode.mapping \
    %{buildroot}%{modsec_prefix}/share/unicode.mapping

if [ -d %{buildroot}%{_includedir}/modsecurity ]; then
    rm -rf %{buildroot}%{modsec_prefix}/include/modsecurity
    mv %{buildroot}%{_includedir}/modsecurity %{buildroot}%{modsec_prefix}/include/
fi

if [ -d %{buildroot}%{_includedir}/modsecurity_test ]; then
    rm -rf %{buildroot}%{modsec_prefix}/include/modsecurity_test
    mv %{buildroot}%{_includedir}/modsecurity_test %{buildroot}%{modsec_prefix}/include/
fi

if [ -d %{buildroot}%{_libdir}/pkgconfig ]; then
    find %{buildroot}%{_libdir}/pkgconfig -maxdepth 1 -name '*.pc' -exec mv -f {} %{buildroot}%{modsec_prefix}/lib64/pkgconfig/ \;
fi

if ls %{buildroot}%{_libdir}/libmodsecurity.so* >/dev/null 2>&1; then
    mv -f %{buildroot}%{_libdir}/libmodsecurity.so* %{buildroot}%{modsec_prefix}/lib64/
fi

find %{buildroot} -name '*.la' -type f -delete
rm -f %{buildroot}%{modsec_prefix}/lib64/libmodsecurity.a
rm -f %{buildroot}%{_libdir}/libmodsecurity.a

[ -d %{buildroot}%{_includedir} ] && find %{buildroot}%{_includedir} -type d -empty -delete || :
[ -d %{buildroot}%{_libdir}/pkgconfig ] && find %{buildroot}%{_libdir}/pkgconfig -type d -empty -delete || :
[ -d %{buildroot}%{_libdir} ] && find %{buildroot}%{_libdir} -type d -empty -delete || :

mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
cat > %{buildroot}%{_sysconfdir}/ld.so.conf.d/modsecurity.conf <<'EOF'
/opt/modsecurity/lib64
EOF

test -d %{buildroot}%{modsec_prefix}/include/modsecurity || {
    echo "ERROR: headers are missing under %{modsec_prefix}/include/modsecurity"
    echo "Installed files:"
    find %{buildroot} -maxdepth 8 -type f | sort
    exit 1
}

test -f %{buildroot}%{modsec_prefix}/lib64/libmodsecurity.so || {
    echo "ERROR: libmodsecurity.so is missing under %{modsec_prefix}/lib64"
    echo "Installed files:"
    find %{buildroot} -maxdepth 8 -type f | sort
    exit 1
}

ls %{buildroot}%{modsec_prefix}/lib64/libmodsecurity.so.* >/dev/null 2>&1 || {
    echo "ERROR: libmodsecurity shared object version is missing under %{modsec_prefix}/lib64"
    echo "Installed files:"
    find %{buildroot} -maxdepth 8 -type f | sort
    exit 1
}

ls %{buildroot}%{modsec_prefix}/lib64/pkgconfig/*.pc >/dev/null 2>&1 || {
    echo "ERROR: pkg-config file is missing under %{modsec_prefix}/lib64/pkgconfig"
    echo "Installed files:"
    find %{buildroot} -maxdepth 8 -type f | sort
    exit 1
}

test -f %{buildroot}%{modsec_prefix}/share/modsecurity.conf-recommended || {
    echo "ERROR: modsecurity.conf-recommended is missing under %{modsec_prefix}/share"
    echo "Installed files:"
    find %{buildroot} -maxdepth 8 -type f | sort
    exit 1
}

test -f %{buildroot}%{modsec_prefix}/share/unicode.mapping || {
    echo "ERROR: unicode.mapping is missing under %{modsec_prefix}/share"
    echo "Installed files:"
    find %{buildroot} -maxdepth 8 -type f | sort
    exit 1
}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license LICENSE
%doc README.md

%{modsec_prefix}
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/modsecurity.conf

%changelog
* Wed Jul 01 2026 Akiyoshi Kurita <weibu@redadmin.org> - 3.0.16-1
- Update to ModSecurity v3.0.16
- Rebuild complete source archive with submodules

* Sun Jun 21 2026 Akiyoshi Kurita <weibu@redadmin.org> - 3.0.15-2
- Install modsecurity.conf-recommended and unicode.mapping under /opt/modsecurity/share
- Keep nginx configuration under manual control

* Sat Jun 20 2026 Akiyoshi Kurita <weibu@redadmin.org> - 3.0.15-1
- Build ModSecurity v3 under /opt/modsecurity
- Include runtime and development files in one RPM
- Use submodule-expanded source archive
- Normalize headers, libraries, and pkg-config files under /opt/modsecurity
- Package the whole /opt/modsecurity tree
- Remove static archive files
