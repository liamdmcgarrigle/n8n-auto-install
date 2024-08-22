from utils import run_command
import os
import base64
import requests
import subprocess
import platform
import tldextract


def create_cf_tunnel(domain, account_id, token):
    tunnel_secret = base64.b64encode(os.urandom(32)).decode('utf-8')

    
    # Create Tunnel
    print("\nCreating Cloudflare Tunnel in account...")
    cf_create_response = _create_tunnel(domain, account_id, token, tunnel_secret)
    print(f"Tunnel '{cf_create_response['result']['name']}' created successfully")
    
    tunnel_id = cf_create_response["result"]["id"]
    tunnel_token = cf_create_response["result"]["token"]

    # Add Config to Tunnel
    print("\nAdding configuration to Cloudflare Tunnel...")
    _add_domain_to_tunel(tunnel_id, domain, account_id, token)
    print("Tunnel configuration updated successfully")

    print(f"\nPointing {domain} DNS records to Cloudflare Tunnel...")
    _add_tunnel_dns_records(tunnel_id, domain, account_id, token)
    print("DNS records updated successfully")


    # Start docker container that connects tunnel
    print("\nStarting Cloudflare Tunnel Docker Container...")
    _run_cf_docker_tunnel(tunnel_token)
    print("Container successfully started")
    print(f"visit https://{domain} to test it out\n")




def _create_tunnel(domain, account_id, token, tunnel_secret):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel"

    tunnel_name = f'n8n {domain} tunnel'

    payload = {
        "config_src": "cloudflare",
        "name": tunnel_name,
        "tunnel_secret": tunnel_secret
    }

    headers = {
        'Content-Type': "application/json",
        'Authorization': f"Bearer {token}"
    }

    

    response = requests.post(url, headers=headers, json=payload)

    # Check for a successful response
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to create tunnel. Status code: {response.status_code}")
        print(response.json())
        exit()




def _add_domain_to_tunel(tunnel_id, domain, account_id, token):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations"

    local_ip = _get_local_ip()

    payload = {
        "config": {
            "ingress": [
                {
                    "hostname":domain,
                    "service": f"http://{local_ip}:5678"
                },
                {
                    "service": f"http_status:404"
                }
            ],
        }
    }

    headers = {
        'Content-Type': "application/json",
        'Authorization': f"Bearer {token}"
    }

    response = requests.put(url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to update tunnel configuration. Status code: {response.status_code}")
        exit()


def _find_dns_zone_id(domain, account_id, token):
    url = "https://api.cloudflare.com/client/v4/zones"


    extracted = tldextract.extract(domain)
    search_domain = f"{extracted.domain}.{extracted.suffix}"

    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "name": search_domain,  # This will use the 'equal' operator by default
        "account.id": account_id
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        
        data = response.json()
        
        if data["success"] and data["result"]:
            # Return the ID of the first (and should be only) matching zone
            return data["result"][0]["id"]
        else:
            print(f"No zone found for domain: {domain}")
            exit()
    
    except requests.RequestException as e:
        print(f"Error fetching zone ID: {e}")
        if response:
            print(f"Response content: {response.text}")
        raise


def _add_tunnel_dns_records(tunnel_id, domain, account_id, token):

    zone_id = _find_dns_zone_id(domain, account_id, token)

    # Parse the domain
    extracted = tldextract.extract(domain)
    if extracted.subdomain:
        name = extracted.subdomain
    else:
        name = '@'

    # Generate a base64 ID
    id = base64.b64encode(os.urandom(32)).decode('utf-8')

    # Set the content to the tunnel URL
    content = f"{tunnel_id}.cfargotunnel.com"

    # Prepare the payload
    payload = {
        "type": "CNAME",
        "name": name,
        "content": content,
        "ttl": 1, 
        "proxied": True,
        "comment": f"Added by automatic tunnel setup script for tunnel ID: {tunnel_id}",
        "id": id
    }

    # Prepare the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Make the API request
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        return response.json()
    except requests.RequestException as e:
        print(f"Error adding DNS record: {e}")
        if response:
            print(f"Response content: {response.text}")
        raise




def _run_cf_docker_tunnel(tunnel_token):
    # run docker from token returned from creation

    run_command(f"sudo docker run -d cloudflare/cloudflared:latest tunnel --no-autoupdate run --token {tunnel_token}")



def _get_local_ip():
    """
    Get the local IP address of the machine.

    This function works on both Linux and macOS systems. It uses different
    commands based on the operating system to retrieve the IP address.

    Returns:
        str: The local IP address of the machine.

    Raises:
        RuntimeError: If unable to determine the IP address.
    """
    system = platform.system()

    try:
        if system == "Linux":
            # For Linux, use ip route command
            command = "ip route get 1 | awk '{print $7; exit}'"
            ip = subprocess.check_output(command, shell=True, universal_newlines=True).strip()
        elif system == "Darwin":  # macOS
            # For macOS, use ifconfig command
            command = "ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1"
            ip = subprocess.check_output(command, shell=True, universal_newlines=True).strip()
        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

        if not ip:
            raise RuntimeError("Unable to determine IP address")

        return ip

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running command: {e}")
    except Exception as e:
        raise RuntimeError(f"Error determining IP address: {e}")