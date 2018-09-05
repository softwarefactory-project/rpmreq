Name:             foo
Version:          0.42.0
Release:          1%{?dist}
Summary:          Tools for lulz

Group:            Development/Languages
License:          ASL 2.0
URL:              https://github.com/softwarefactory-project/foo/
Source0:          https://pypi.io/packages/source/f/%{name}/%{name}-%{version}.tar.gz

BuildArch:        noarch

BuildRequires:    git
BuildRequires:    bar == 1.2.3
BuildRequires:    asciidoc >= 0.1
BuildRequires:    python

Requires:         python2-foo == %{version}-%{release}

%description
Lorem Ipsum dolor sit amet...

%package -n python2-foo
Summary:          Tools for lulz
%{?python_provide:%python_provide python2-foo}

BuildRequires:    python2-devel
BuildRequires:    python-setuptools
BuildRequires:    python-pbr
BuildRequires:    PyYAML
%if 0
BuildRequires:    python2-macro-disabled-breq
%endif
%if 1
BuildRequires:    python2-macro-enabled-breq
%endif

Requires:         python2-future
Requires:         python2-pbr
Requires:         python-pymod2pkg >= 0.2.1

%description -n python2-foo
Lorem Ipsum dolor sit amet python 2...

%if 0%{?with_python3}
%package -n python3-foo
Summary:          Tools for lulz
%{?python_provide:%python_provide python3-foo}

BuildRequires:    python3-devel
BuildRequires:    python3-setuptools
BuildRequires:    python3-pbr
BuildRequires:    python3-PyYAML

Requires:         python3-future
Requires:         python3-pbr
Requires:         python3-pymod2pkg >= 0.2.1

%description -n python3-foo
Lorem Ipsum dolor sit amet python 3...
%endif


%prep
%autosetup -n %{name}-%{version} -S git

# We handle requirements ourselves, pkg_resources only bring pain
rm -rf requirements.txt test-requirements.txt

%build
%py2_build

%if 0%{?with_python3}
%py3_build
%endif

%install
%if 0%{?with_python3}
%py3_install
mv %{buildroot}%{_bindir}/foo %{buildroot}%{_bindir}/rdopkg-%{python3_version}
ln -s ./foo-%{python3_version} %{buildroot}%{_bindir}/rdopkg-3
%endif

%py2_install
ln -s ./foo %{buildroot}%{_bindir}/rdopkg-%{python2_version}
ln -s ./foo %{buildroot}%{_bindir}/rdopkg-2

make doc


%files -n foo
%doc README.md
%{_bindir}/foo

%files -n python2-foo
%license LICENSE
%{_bindir}/foo-2
%{_bindir}/foo-%{python2_version}
%{python2_sitelib}/foo
%{python2_sitelib}/*.egg-info

%if 0%{?with_python3}
%files -n python3-foo
%license LICENSE
%{_bindir}/foo-3
%{_bindir}/foo-%{python3_version}
%{python3_sitelib}/foo
%{python3_sitelib}/*.egg-info
%endif


%changelog
* Wed Sep 05 2018 Jakub Ruzicka <jruzicka@redhat.com> 0.42.0-1
- First changelog entry
- Stuff, things, ...

* Mon Sep 03 2018 Jakub Ruzicka <jruzicka@redhat.com> 0.41.0-2
- Second changelog entry
