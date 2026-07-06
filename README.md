# ModSecurity RPM for EL7

This repository provides an unofficial RPM package for ModSecurity v3 on EL7.

This package is intended for testing and verification of Nginx WAF integration using the ModSecurity-nginx connector.

## Overview

This RPM installs ModSecurity under:

    /opt/modsecurity

Example runtime library path:

    /opt/modsecurity/lib64/libmodsecurity.so.3

The package includes:

- ModSecurity runtime libraries
- ModSecurity headers
- pkg-config files
- example configuration files
- ldconfig configuration for `/opt/modsecurity/lib64`

This package can be used together with an Nginx build that includes the ModSecurity-nginx connector.

## Repository Layout

    README.md
    SPEC/
    RPMS/
    Logs/

RPM files are stored under:

    RPMS/

## Install

Install the built RPM package with:

    sudo yum localinstall RPMS/*.rpm

If RPM files are stored under an architecture subdirectory, use:

    sudo yum localinstall RPMS/x86_64/*.rpm

A more general command is:

    sudo yum localinstall $(find RPMS -type f -name '*.rpm' | sort)

## Verify Installation

Check installed files:

    rpm -ql modsecurity | grep /opt/modsecurity

Check that the runtime library is visible to the dynamic linker:

    ldconfig -p | grep libmodsecurity

Expected example:

    libmodsecurity.so.3 => /opt/modsecurity/lib64/libmodsecurity.so.3

If the library does not appear, run:

    sudo ldconfig

## Example Paths

Main installation directory:

    /opt/modsecurity

Library directory:

    /opt/modsecurity/lib64

Header directory:

    /opt/modsecurity/include

pkg-config directory:

    /opt/modsecurity/lib64/pkgconfig

Example configuration files:

    /opt/modsecurity/share/modsecurity.conf-recommended
    /opt/modsecurity/share/unicode.mapping

ldconfig configuration:

    /etc/ld.so.conf.d/modsecurity.conf

## Nginx Integration Notes

This package only installs ModSecurity itself.

To use ModSecurity with Nginx, Nginx must be built with the ModSecurity-nginx connector.

When building Nginx, make sure the build can find ModSecurity under:

    /opt/modsecurity

For example:

    export PKG_CONFIG_PATH=/opt/modsecurity/lib64/pkgconfig

Confirm that Nginx was built with the ModSecurity-nginx connector:

    nginx -V 2>&1 | grep -i modsecurity

Expected output should include:

    --add-module=ModSecurity-nginx

Confirm that Nginx resolves `libmodsecurity.so.3`:

    ldd /usr/sbin/nginx | grep modsecurity

Expected example:

    libmodsecurity.so.3 => /opt/modsecurity/lib64/libmodsecurity.so.3

## ModSecurity Rule Engine

Before enabling blocking mode in production, it is recommended to run ModSecurity in detection-only mode and review logs carefully.

Example:

    SecRuleEngine DetectionOnly

After sufficient verification, blocking mode can be enabled if appropriate.

    SecRuleEngine On

## Basic Configuration Example

Create an Nginx ModSecurity configuration directory:

    sudo mkdir -p /etc/nginx/modsec

Copy the recommended configuration:

    sudo cp /opt/modsecurity/share/modsecurity.conf-recommended /etc/nginx/modsec/modsecurity.conf
    sudo cp /opt/modsecurity/share/unicode.mapping /etc/nginx/modsec/unicode.mapping

For initial testing, set detection-only mode:

    sudo sed -i 's/^SecRuleEngine .*/SecRuleEngine DetectionOnly/' /etc/nginx/modsec/modsecurity.conf

Example `/etc/nginx/modsec/main.conf`:

    Include /etc/nginx/modsec/modsecurity.conf

Example Nginx server configuration:

    server {
        listen 80;
        server_name example.local;

        modsecurity on;
        modsecurity_rules_file /etc/nginx/modsec/main.conf;

        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
        }
    }

Test Nginx configuration:

    sudo nginx -t

Restart Nginx:

    sudo systemctl restart nginx

## OWASP Core Rule Set

OWASP Core Rule Set is not bundled in this package.

CRS should be installed or placed manually.

A typical include layout is:

    Include /etc/nginx/modsec/modsecurity.conf
    Include /etc/nginx/modsec/crs-setup.conf
    Include /etc/nginx/modsec/rules/*.conf

For initial operation, OWASP CRS 3.3.x is recommended because it is stable and easier to validate with ModSecurity v3.

CRS 4.x may work, but it should be validated separately before production use.

## Simple Test

After Nginx is configured with ModSecurity and blocking mode is enabled, a simple SQL injection test can be used:

    curl -i 'http://127.0.0.1/?id=1%20UNION%20SELECT%201,2,3'

Expected result when blocking is active:

    HTTP/1.1 403 Forbidden

If the request is detected but still returns `200`, check CRS blocking evaluation and local exclusions.

## Target Environment

Tested target environment:

    EL7 x86_64
    ModSecurity v3.0.16
    Nginx with ModSecurity-nginx connector

Build environment:

    Build Tool: mock
    Mock Config: centos+epel-7-x86_64

This build may require a newer compiler toolchain than the default EL7 GCC, depending on the ModSecurity source version.

## Production Notes

Do not enable blocking mode directly in production without verification.

Recommended rollout:

1. Install this ModSecurity RPM.
2. Install or use an Nginx build with ModSecurity-nginx support.
3. Configure OWASP CRS manually.
4. Start with `SecRuleEngine DetectionOnly`.
5. Review audit logs.
6. Add local exclusions for false positives.
7. Enable `SecRuleEngine On` after validation.
8. Keep CRS configuration and local exclusions under version control.

ModSecurity and CRS should be treated as one layer of defense, not as a replacement for application fixes, patching, access control, rate limiting, or regular security updates.

## Disclaimer

This repository is unofficial.

It is not provided, maintained, endorsed, or supported by AlmaLinux OS Foundation, CentOS, Red Hat, OWASP, Trustwave, ModSecurity, nginx.org, or any upstream project.

Use this repository at your own risk.

The author provides no warranty of any kind.

Please test carefully in a verification environment before using it in production.

## License

ModSecurity is licensed under the Apache License 2.0.

See the upstream ModSecurity project for details:

    https://github.com/owasp-modsecurity/ModSecurity

Packaging files in this repository are provided for RPM build and integration testing purposes.

Unless otherwise stated, packaging files in this repository are released under the Apache License 2.0.
