%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%define mod_name keystone
%define py_puresitedir  /usr/lib/python2.6/site-packages

Name:           openstack-keystone
Release:        20111205.1382.5c70d24%{?dist}
Version:	2012.1
Url:            http://www.openstack.org
Summary:        OpenStack Identity Service
License:        Apache 2.0
Vendor:         USC/ISI
Group:          Development/Languages/Python
Source0:          http://openstack-keystone.openstack.org/tarballs/%{name}-%{version}.tar.gz  
Source1:        %{name}.init
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel python-setuptools >= 0.6.0
BuildArch:      noarch
Requires:       python-eventlet python-lxml python-paste python-sqlalchemy python-routes python-httplib2 python-paste-deploy start-stop-daemon python-webob python-setuptools python-passlib

%description
The Keystone project provides services for authenticating and managing user,
account, and role information for OpenStack clouds running on OpenStack
Compute and as an authorization service for OpenStack Object Storage.

%prep
%setup -q -n %{name}-%{version}
sed -i 's|sqlite:///keystone|sqlite:////var/lib/keystone/keystone|' etc/keystone.conf
sed -i 's|log_file = keystone.log|log_file = /var/log/keystone/keystone.log|' etc/keystone.conf

%build
python setup.py build

%install
%__rm -rf %{buildroot}

# Don't make documentation
# %__make -C doc/ html PYTHONPATH=%{_builddir}/%{name}-%{version}
python setup.py install --prefix=%{_prefix} --root=%{buildroot}

install -d -m 755 %{buildroot}%{_sysconfdir}/%{mod_name}
install -m 644 etc/* %{buildroot}%{_sysconfdir}/%{mod_name}
install -d -m 755 %{buildroot}%{_sysconfdir}/nova
install -m 644 examples/paste/auth_*ini %{buildroot}%{_sysconfdir}/nova
install -m 644 examples/paste/nova-api-paste.ini %{buildroot}%{_sysconfdir}/nova/api-paste.ini.keystone.example

install -d -m 755 %{buildroot}%{_sharedstatedir}/keystone
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{mod_name}
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{mod_name}

install -p -D -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}

%__rm -rf %{buildroot}%{py_puresitedir}/{doc,examples}
%__rm %{buildroot}%{py_puresitedir}/tools/pip-requires*

%clean
%__rm -rf %{buildroot}

%pre
getent passwd keystone >/dev/null || \
useradd -r -g nobody -G nobody -d %{_sharedstatedir}/keystone -s /sbin/nologin \
-c "OpenStack Keystone Daemon" keystone
exit 0

%preun
if [ $1 = 0 ] ; then
    /sbin/service %{name} stop
    /sbin/chkconfig --del %{name}
fi

%files
%defattr(-,root,root,-)
%{_sysconfdir}
%doc README.md HACKING LICENSE examples doc
%{py_puresitedir}/%{mod_name}*
%{py_puresitedir}/tools
%{_usr}/bin
%dir %attr(0755, keystone, nobody) %{_sharedstatedir}/%{mod_name}
%dir %attr(0755, keystone, nobody) %{_localstatedir}/log/%{mod_name}
%dir %attr(0755, keystone, nobody) %{_localstatedir}/run/%{mod_name}

%changelog
