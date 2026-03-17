Name:           osprey
Version:        1.5.2
Release:        1%{?dist}
Summary:        The Osprey: High-Performance ClamAV Signature & Hashing Suite

License:        GPLv2 [cite: 26, 43-50]
URL:            https://www.clamav.net/
Source0:        osprey-backend-1.5.2.tar.gz
Source1:        osprey-view.py
Source2:        osprey.desktop
Source3:        osprey-update.service
Source4:        osprey-icon.png

BuildRequires:  gcc, cmake, make, openssl-devel, zlib-devel, json-c-devel 
BuildRequires:  libcurl-devel, ncurses-devel, sendmail-milter-devel, systemd-devel
Requires:       python3-pyqt6, openssl, zlib, libcurl, ncurses, systemd

%description
The Osprey provides a professional PyQt6 interface for ClamAV's backend logic. 
It features digital signature verification [cite: 305-316], SHA2-256 hashing [cite: 211-221], 
and Virus Database (CVD) header inspection .

%prep
%autosetup -n clamav-1.5.2

%build
# Use Fedora's cmake macro with RPATH stripping enabled 
%cmake \
    -DJSONC_INCLUDE_DIR=/usr/include/json-c \
    -DJSONC_LIBRARY=/usr/lib64/libjson-c.so \
    -DENABLE_JSON_SHARED=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=OFF
%cmake_build --target sigtool

%install
# 1. Install the C backend binary from the Fedora-specific build path [cite: 27-29]
mkdir -p %{buildroot}%{_bindir}
install -m 755 %{_vpath_builddir}/sigtool/sigtool %{buildroot}%{_bindir}/osprey-backend

# 2. Install the Python GUI and support files
install -m 755 %{SOURCE1} %{buildroot}%{_bindir}/osprey-view
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 %{SOURCE2} %{buildroot}%{_datadir}/applications/osprey.desktop

# 3. Install Systemd service and App Icon
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/osprey-update.service 
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/
install -m 644 %{SOURCE4} %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/osprey-icon.png

%post
%systemd_post osprey-update.service

%preun
%systemd_preun osprey-update.service

%postun
%systemd_postun_with_restart osprey-update.service

%files
%{_bindir}/osprey-backend
%{_bindir}/osprey-view
%{_datadir}/applications/osprey.desktop
%{_datadir}/icons/hicolor/48x48/apps/osprey-icon.png
%{_unitdir}/osprey-update.service

%changelog
* Tue Mar 17 2026 Daniel Stevens <daniel@example.com> - 1.5.2-1
- Finalized Fedora build with RPATH stripping and JSON-C manual paths.
