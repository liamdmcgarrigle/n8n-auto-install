# How to use

Just run the command 
```
curl -sSL https://raw.githubusercontent.com/liamdmcgarrigle/n8n-auto-install/main/install.sh | bash && bash n8n-auto-install/setup.sh
```

Then you will just need to answer the questions that are prompted

------ ADD A GIF HERE OF THE QUESTIONS AND ANSWERS ------

## What it does

> ⚠️  This is a quick and dirty solution. It is essentially copy and pasting config files, but based on your answers. Any maintenance or updates will need to be done manually. I show simple examples of that in this readme.

1. downloads dependencies (if they aren't already installed)
    - python
    - python3-ven
    - pip
    - git
    - docker
2. Clones this github repo to your system
3. Generates an `/n8n` folder with `docker-compose.yaml`, `.env`, and a `dockerfile` based on your inputs.
4. Starts the docker container (and builds first if needed)
5. Automatically sets up a Cloudflare tunnel and sets Cloudflare DNS records with your Cloudflare token (if you select that option)
6. Deletes itself from your machine

# Maintenance and Trouble Shooting
If you are using this because you don't 

## Commands you need to know
### `cd`
`cd` is to change directory. If you are at the root of your system, and you have a folder named `/n8n`, you can go to that folder with `cd n8n`. Then to go back, you can run `cd ..`. A `.` brings you back in the file system.

Your current directory is shown to the left of your command input, with a `~` notating the root.

### `ls` and `ls -a`
`ls` lists files and `ls -a` lists files including hidden files (files and folders starting with a `.` are hidden, like the `.env` file). 

### `rm` & `rm -r`
These are commands to delete files and folders. 
If you are in a directory that has a file called `dockerfile` in it, you can run `rm dockerfile` and it will delete.
If you want to delete a folder with the items inside of it you can run `rm -rf folder-name`. 

# Supported OS
This script supports all Linux distros supported with the [official install script](https://github.com/docker/docker-install) and Mac. This does not support Windows. If using Windows, run on WSL (though i did not test there).

# Cloudflare Tunnel Required Info
1. Your domain needs to be managed on Cloudflare
It does not need to be registered there, just managed. It is free.

2. Create an API Token
Go to [https://dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens) to create a token. You need the `Cloudflare Tunnel:Edit` and `DNS:Edit` scopes.

3. Get Account ID
Go to [your CloudFlare Dashboard](https://dash.cloudflare.com/). The ID in the URL is your account ID.

![account id screenshot](./images/cloudflare_account_id.png)
