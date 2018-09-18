%global service macros

Name:             %{service}-basic
Version:          0.42.0
Release:          1%{?dist}
Summary:          Dem macroz

Group:            Development/Languages
License:          ASL 2.0
URL:              https://github.com/softwarefactory-project/basic-macros/
Source0:          https://pypi.io/packages/source/b/%{name}/%{name}-%{version}.tar.gz

Source1:          %{service}-api.service

BuildArch:        noarch

BuildRequires:    build-%{service}
BuildRequires:    git

Requires:         runtime-%{service}
Requires:         tig
