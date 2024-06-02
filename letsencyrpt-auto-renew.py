import ssl
import socket
from datetime import datetime
import subprocess

def get_ssl_expiry_date(hostname):
    port = '443'
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            expiry_date_str = cert['notAfter']
            expiry_date = datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
            return expiry_date

def check_and_renew_certificate(hostname):
    expiry_date = get_ssl_expiry_date(hostname)
    current_date = datetime.utcnow()
    days_until_expiry = (expiry_date - current_date).days

    print(f"The SSL certificate for {hostname} expires on {expiry_date}")
    print(f"Current date is {current_date}")
    print(f"Days until expiry: {days_until_expiry}")

    if days_until_expiry <= 2:
        print("The SSL certificate expires within 2 days. Renewing...")
        renew_certificate(hostname)
    else:
        print("The SSL certificate does not expire within 2 days. No action needed.")

def renew_certificate(hostname):
    try:
        command = f"certbot certonly --force-renewal --non-interactive --standalone -d {hostname}"
        subprocess.run(command, shell=True, check=True)
        print(f"Certificate renewal process for {hostname} initiated.")
        
        # Reload Nginx after renewing the certificate
        reload_nginx()
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to renew the certificate for {hostname}: {e}")

def reload_nginx():
    try:
        command = "systemctl reload nginx"
        subprocess.run(command, shell=True, check=True)
        print("Nginx reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while reloading Nginx: {e}")

# Example usage
hostname = 'mail.medilynq.com'
check_and_renew_certificate(hostname)
