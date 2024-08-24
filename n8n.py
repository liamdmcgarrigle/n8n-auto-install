import re
from utils import run_command, create_file


def start_n8n_container(env_vars, is_custom_image, list_of_packages = None):

    print("\nCreating config files...")
    # Creates n8n folder one folder back
    run_command("mkdir n8n")

    # Creates .env file with all our vars
    vars = _create_env_file(env_vars)

    # Create .env file
    create_file("n8n/.env", vars["env_vars"])

    # Create docker-compose.yaml file based on custom image
    if not is_custom_image:
        # Create docker compose file with default image
        create_file("n8n/docker-compose.yaml", _create_dockercompose_file(vars["dockercompose_vars"], False))
    else:
        # create docker compose file with custom image
        create_file("n8n/docker-compose.yaml", _create_dockercompose_file(vars["dockercompose_vars"], True))
        # create docker file to build the image
        create_file("n8n/dockerfile", _create_dockerfile(list_of_packages or ""))
        # create docker entrypoint file
        create_file("n8n/docker-entrypoint.sh", _create_docker_entrypoint())
        # make docker entrypoint file executable
        run_command("cd n8n && sudo chmod +x docker-entrypoint.sh")
    print("Files created")

    # Build image
    if is_custom_image:
        print("\nBuilding image. This might take a few minutes...")
        run_command("cd n8n &&  docker compose build")
        print("\nImage build complete.")

    # Run container
    print("\nStarting container. This might take a minute...")
    run_command("cd n8n &&  docker compose up -d")
    print("Container started. It should now be locally avalible at http://localhost:5678")



def _create_env_file(env_vars):

    env_template = f"""
# See Vars at https://docs.n8n.io/hosting/configuration/environment-variables/
# File setup by an automated script by liam@teraprise.io found here https://github.com/liamdmcgarrigle/n8n-auto-install

# N8N VERSION
N8N_VERSION="latest"

# AI VARIABLES


# CREDENTIALS VARIABLES
CREDENTIALS_DEFAULT_NAME="{env_vars['CREDENTIALS_DEFAULT_NAME']}"

# DATABASE VARIABLES
DB_TYPE="{env_vars['DB_TYPE']}"
DB_TABLE_PREFIX="{env_vars['DB_TABLE_PREFIX']}"
DB_SQLITE_VACUUM_ON_STARTUP="{env_vars['DB_SQLITE_VACUUM_ON_STARTUP']}"

# DEPLOYMENT VARIABLES
N8N_EDITOR_BASE_URL="{env_vars['N8N_EDITOR_BASE_URL']}"
N8N_PERSONALIZATION_ENABLED="{env_vars['N8N_PERSONALIZATION_ENABLED']}"
N8N_CONFIG_FILES="{env_vars['N8N_CONFIG_FILES']}"
N8N_DISABLE_UI="{env_vars['N8N_DISABLE_UI']}"
N8N_PREVIEW_MODE="{env_vars['N8N_PREVIEW_MODE']}"
N8N_TEMPLATES_ENABLED="{env_vars['N8N_TEMPLATES_ENABLED']}"
N8N_TEMPLATES_HOST="{env_vars.get('N8N_TEMPLATES_HOST')}"
N8N_ENCRYPTION_KEY="{env_vars['N8N_ENCRYPTION_KEY']}"
N8N_GRACEFUL_SHUTDOWN_TIMEOUT="{env_vars['N8N_GRACEFUL_SHUTDOWN_TIMEOUT']}"
N8N_PUBLIC_API_DISABLED="{env_vars['N8N_PUBLIC_API_DISABLED']}"
N8N_HIRING_BANNER_ENABLED="{env_vars['N8N_HIRING_BANNER_ENABLED']}"

# BINARY DATA 
N8N_AVAILABLE_BINARY_DATA_MODES="{env_vars['N8N_AVAILABLE_BINARY_DATA_MODES']}"
N8N_BINARY_DATA_STORAGE_PATH="{env_vars['N8N_BINARY_DATA_STORAGE_PATH']}"
N8N_DEFAULT_BINARY_DATA_MODE="{env_vars['N8N_DEFAULT_BINARY_DATA_MODE']}"

# USER MANAGEMENT 
#  SMTP EMAIL
N8N_EMAIL_MODE="{env_vars['N8N_EMAIL_MODE']}"
N8N_SMTP_HOST="{env_vars['N8N_SMTP_HOST']}"
N8N_SMTP_PORT="{env_vars['N8N_SMTP_PORT']}"
N8N_SMTP_USER="{env_vars['N8N_SMTP_USER']}"
N8N_SMTP_PASS="{env_vars['N8N_SMTP_PASS']}"
#  SERVICE ACCOUNT EMAIL
N8N_SMTP_OAUTH_SERVICE_CLIENT="{env_vars['N8N_SMTP_OAUTH_SERVICE_CLIENT']}"
N8N_SMTP_OAUTH_PRIVATE_KEY="{env_vars['N8N_SMTP_OAUTH_PRIVATE_KEY']}"
N8N_SMTP_SENDER="{env_vars['N8N_SMTP_SENDER']}"
#  Templates
N8N_UM_EMAIL_TEMPLATES_INVITE="{env_vars['N8N_UM_EMAIL_TEMPLATES_INVITE']}"
N8N_UM_EMAIL_TEMPLATES_PWRESET="{env_vars['N8N_UM_EMAIL_TEMPLATES_PWRESET']}"
N8N_UM_EMAIL_TEMPLATES_WORKFLOW_SHARED="{env_vars['N8N_UM_EMAIL_TEMPLATES_WORKFLOW_SHARED']}"
N8N_UM_EMAIL_TEMPLATES_CREDENTIALS_SHARED="{env_vars['N8N_UM_EMAIL_TEMPLATES_CREDENTIALS_SHARED']}"
#  Token options
N8N_USER_MANAGEMENT_JWT_SECRET="{env_vars['N8N_USER_MANAGEMENT_JWT_SECRET']}"
N8N_USER_MANAGEMENT_JWT_DURATION_HOURS="{env_vars['N8N_USER_MANAGEMENT_JWT_DURATION_HOURS']}"
N8N_USER_MANAGEMENT_JWT_REFRESH_TIMEOUT_HOURS="{env_vars['N8N_USER_MANAGEMENT_JWT_REFRESH_TIMEOUT_HOURS']}"
N8N_MFA_ENABLED="{env_vars['N8N_MFA_ENABLED']}"

# ENDPOINTS
N8N_PAYLOAD_SIZE_MAX="{env_vars['N8N_PAYLOAD_SIZE_MAX']}"
N8N_METRICS="{env_vars['N8N_METRICS']}"
N8N_METRICS_PREFIX="{env_vars['N8N_METRICS_PREFIX']}"
N8N_METRICS_INCLUDE_DEFAULT_METRICS="{env_vars['N8N_METRICS_INCLUDE_DEFAULT_METRICS']}"
N8N_METRICS_INCLUDE_CACHE_METRICS="{env_vars['N8N_METRICS_INCLUDE_CACHE_METRICS']}"
N8N_METRICS_INCLUDE_MESSAGE_EVENT_BUS_METRICS="{env_vars['N8N_METRICS_INCLUDE_MESSAGE_EVENT_BUS_METRICS']}"
N8N_METRICS_INCLUDE_WORKFLOW_ID_LABEL="{env_vars['N8N_METRICS_INCLUDE_WORKFLOW_ID_LABEL']}"
N8N_METRICS_INCLUDE_NODE_TYPE_LABEL="{env_vars['N8N_METRICS_INCLUDE_NODE_TYPE_LABEL']}"
N8N_METRICS_INCLUDE_CREDENTIAL_TYPE_LABEL="{env_vars['N8N_METRICS_INCLUDE_CREDENTIAL_TYPE_LABEL']}"
N8N_METRICS_INCLUDE_API_ENDPOINTS="{env_vars['N8N_METRICS_INCLUDE_API_ENDPOINTS']}"
N8N_METRICS_INCLUDE_API_PATH_LABEL="{env_vars['N8N_METRICS_INCLUDE_API_PATH_LABEL']}"
N8N_METRICS_INCLUDE_API_METHOD_LABEL="{env_vars['N8N_METRICS_INCLUDE_API_METHOD_LABEL']}"
N8N_METRICS_INCLUDE_API_STATUS_CODE_LABEL="{env_vars['N8N_METRICS_INCLUDE_API_STATUS_CODE_LABEL']}"
N8N_ENDPOINT_REST="{env_vars['N8N_ENDPOINT_REST']}"
N8N_ENDPOINT_WEBHOOK="{env_vars['N8N_ENDPOINT_WEBHOOK']}"
N8N_ENDPOINT_WEBHOOK_TEST="{env_vars['N8N_ENDPOINT_WEBHOOK_TEST']}"
N8N_ENDPOINT_WEBHOOK_WAIT="{env_vars['N8N_ENDPOINT_WEBHOOK_WAIT']}"
WEBHOOK_URL="{env_vars['WEBHOOK_URL']}"
N8N_DISABLE_PRODUCTION_MAIN_PROCESS="{env_vars['N8N_DISABLE_PRODUCTION_MAIN_PROCESS']}"

# EXTERNAL HOOKS
EXTERNAL_HOOK_FILES="{env_vars['EXTERNAL_HOOK_FILES']}"
EXTERNAL_FRONTEND_HOOKS_URLS="{env_vars['EXTERNAL_FRONTEND_HOOKS_URLS']}"

# EXECUTION
EXECUTIONS_MODE="{env_vars['EXECUTIONS_MODE']}"
EXECUTIONS_TIMEOUT="{env_vars['EXECUTIONS_TIMEOUT']}"
EXECUTIONS_TIMEOUT_MAX="{env_vars['EXECUTIONS_TIMEOUT_MAX']}"
EXECUTIONS_DATA_SAVE_ON_ERROR="{env_vars['EXECUTIONS_DATA_SAVE_ON_ERROR']}"
EXECUTIONS_DATA_SAVE_ON_SUCCESS="{env_vars['EXECUTIONS_DATA_SAVE_ON_SUCCESS']}"
EXECUTIONS_DATA_SAVE_ON_PROGRESS="{env_vars['EXECUTIONS_DATA_SAVE_ON_PROGRESS']}"
EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS="{env_vars['EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS']}"
EXECUTIONS_DATA_PRUNE="{env_vars['EXECUTIONS_DATA_PRUNE']}"
EXECUTIONS_DATA_MAX_AGE="{env_vars['EXECUTIONS_DATA_MAX_AGE']}"
EXECUTIONS_DATA_PRUNE_MAX_COUNT="{env_vars['EXECUTIONS_DATA_PRUNE_MAX_COUNT']}"
EXECUTIONS_DATA_HARD_DELETE_BUFFER="{env_vars['EXECUTIONS_DATA_HARD_DELETE_BUFFER']}"
EXECUTIONS_DATA_PRUNE_HARD_DELETE_INTERVAL="{env_vars['EXECUTIONS_DATA_PRUNE_HARD_DELETE_INTERVAL']}"
EXECUTIONS_DATA_PRUNE_SOFT_DELETE_INTERVAL="{env_vars['EXECUTIONS_DATA_PRUNE_SOFT_DELETE_INTERVAL']}"
N8N_CONCURRENCY_PRODUCTION_LIMIT="{env_vars['N8N_CONCURRENCY_PRODUCTION_LIMIT']}"

# LOGS
N8N_LOG_LEVEL="{env_vars['N8N_LOG_LEVEL']}"
N8N_LOG_OUTPUT="{env_vars['N8N_LOG_OUTPUT']}"
N8N_LOG_FILE_COUNT_MAX="{env_vars['N8N_LOG_FILE_COUNT_MAX']}"
N8N_LOG_FILE_SIZE_MAX="{env_vars['N8N_LOG_FILE_SIZE_MAX']}"
N8N_LOG_FILE_LOCATION="{env_vars['N8N_LOG_FILE_LOCATION']}"
DB_LOGGING_ENABLED="{env_vars['DB_LOGGING_ENABLED']}"
DB_LOGGING_OPTIONS="{env_vars['DB_LOGGING_OPTIONS']}"
DB_LOGGING_MAX_EXECUTION_TIME="{env_vars['DB_LOGGING_MAX_EXECUTION_TIME']}"
CODE_ENABLE_STDOUT="{env_vars['CODE_ENABLE_STDOUT']}"

# LOG STREAMING
# N8N_EVENTBUS_CHECKUNSENTINTERVAL="{env_vars['N8N_EVENTBUS_CHECKUNSENTINTERVAL']}"
# N8N_EVENTBUS_LOGWRITER_SYNCFILEACCESS="{env_vars['N8N_EVENTBUS_LOGWRITER_SYNCFILEACCESS']}"
# N8N_EVENTBUS_LOGWRITER_KEEPLOGCOUNT="{env_vars['N8N_EVENTBUS_LOGWRITER_KEEPLOGCOUNT']}"
# N8N_EVENTBUS_LOGWRITER_MAXFILESIZEINKB="{env_vars['N8N_EVENTBUS_LOGWRITER_MAXFILESIZEINKB']}"
# N8N_EVENTBUS_LOGWRITER_LOGBASENAME="{env_vars['N8N_EVENTBUS_LOGWRITER_LOGBASENAME']}"

# EXTERNAL DATA STORAGE
# N8N_EXTERNAL_STORAGE_S3_HOST="{env_vars['N8N_EXTERNAL_STORAGE_S3_HOST']}"
# N8N_EXTERNAL_STORAGE_S3_BUCKET_NAME="{env_vars['N8N_EXTERNAL_STORAGE_S3_BUCKET_NAME']}"
# N8N_EXTERNAL_STORAGE_S3_BUCKET_REGION="{env_vars['N8N_EXTERNAL_STORAGE_S3_BUCKET_REGION']}"
# N8N_EXTERNAL_STORAGE_S3_ACCESS_KEY="{env_vars['N8N_EXTERNAL_STORAGE_S3_ACCESS_KEY']}"
# N8N_EXTERNAL_STORAGE_S3_ACCESS_SECRET="{env_vars['N8N_EXTERNAL_STORAGE_S3_ACCESS_SECRET']}"

# NODES
NODES_INCLUDE="{env_vars['NODES_INCLUDE']}"
NODES_EXCLUDE="{env_vars['NODES_EXCLUDE']}"
NODE_FUNCTION_ALLOW_BUILTIN="{env_vars['NODE_FUNCTION_ALLOW_BUILTIN']}"
NODE_FUNCTION_ALLOW_EXTERNAL="{env_vars['NODE_FUNCTION_ALLOW_EXTERNAL']}"
NODES_ERROR_TRIGGER_TYPE="{env_vars['NODES_ERROR_TRIGGER_TYPE']}"
N8N_CUSTOM_EXTENSIONS="{env_vars['N8N_CUSTOM_EXTENSIONS']}"
N8N_COMMUNITY_PACKAGES_ENABLED="{env_vars['N8N_COMMUNITY_PACKAGES_ENABLED']}"
N8N_COMMUNITY_PACKAGES_REGISTRY="{env_vars['N8N_COMMUNITY_PACKAGES_REGISTRY']}"

# QUEUE MODE
QUEUE_BULL_PREFIX="{env_vars['QUEUE_BULL_PREFIX']}"
QUEUE_BULL_REDIS_DB="{env_vars['QUEUE_BULL_REDIS_DB']}"
QUEUE_BULL_REDIS_HOST="{env_vars['QUEUE_BULL_REDIS_HOST']}"
QUEUE_BULL_REDIS_PORT="{env_vars['QUEUE_BULL_REDIS_PORT']}"
QUEUE_BULL_REDIS_USERNAME="{env_vars['QUEUE_BULL_REDIS_USERNAME']}"
QUEUE_BULL_REDIS_PASSWORD="{env_vars['QUEUE_BULL_REDIS_PASSWORD']}"
QUEUE_BULL_REDIS_TIMEOUT_THRESHOLD="{env_vars['QUEUE_BULL_REDIS_TIMEOUT_THRESHOLD']}"
QUEUE_BULL_REDIS_CLUSTER_NODES="{env_vars['QUEUE_BULL_REDIS_CLUSTER_NODES']}"
QUEUE_BULL_REDIS_TLS="{env_vars['QUEUE_BULL_REDIS_TLS']}"
QUEUE_RECOVERY_INTERVAL="{env_vars['QUEUE_RECOVERY_INTERVAL']}"
QUEUE_HEALTH_CHECK_ACTIVE="{env_vars['QUEUE_HEALTH_CHECK_ACTIVE']}"
QUEUE_HEALTH_CHECK_PORT="{env_vars['QUEUE_HEALTH_CHECK_PORT']}"
QUEUE_WORKER_LOCK_DURATION="{env_vars['QUEUE_WORKER_LOCK_DURATION']}"
QUEUE_WORKER_LOCK_RENEW_TIME="{env_vars['QUEUE_WORKER_LOCK_RENEW_TIME']}"
QUEUE_WORKER_STALLED_INTERVAL="{env_vars['QUEUE_WORKER_STALLED_INTERVAL']}"
QUEUE_WORKER_MAX_STALLED_COUNT="{env_vars['QUEUE_WORKER_MAX_STALLED_COUNT']}"

# SECURITY
N8N_BLOCK_ENV_ACCESS_IN_NODE="{env_vars['N8N_BLOCK_ENV_ACCESS_IN_NODE']}"
N8N_RESTRICT_FILE_ACCESS_TO="{env_vars['N8N_RESTRICT_FILE_ACCESS_TO']}"
N8N_BLOCK_FILE_ACCESS_TO_N8N_FILES="{env_vars['N8N_BLOCK_FILE_ACCESS_TO_N8N_FILES']}"
N8N_SECURITY_AUDIT_DAYS_ABANDONED_WORKFLOW="{env_vars['N8N_SECURITY_AUDIT_DAYS_ABANDONED_WORKFLOW']}"
N8N_SECURE_COOKIE="{env_vars['N8N_SECURE_COOKIE']}"

# GIT
N8N_SOURCECONTROL_DEFAULT_SSH_KEY_TYPE="{env_vars['N8N_SOURCECONTROL_DEFAULT_SSH_KEY_TYPE']}"

# EXTERNAL SECRETS
N8N_EXTERNAL_SECRETS_UPDATE_INTERVAL="{env_vars['N8N_EXTERNAL_SECRETS_UPDATE_INTERVAL']}"

# LOCAL
GENERIC_TIMEZONE="{env_vars['GENERIC_TIMEZONE']}"
N8N_DEFAULT_LOCALE="{env_vars['N8N_DEFAULT_LOCALE']}"

# WORKFLOWS
WORKFLOWS_DEFAULT_NAME="{env_vars['WORKFLOWS_DEFAULT_NAME']}"
N8N_ONBOARDING_FLOW_DISABLED="{env_vars['N8N_ONBOARDING_FLOW_DISABLED']}"
N8N_WORKFLOW_TAGS_DISABLED="{env_vars['N8N_WORKFLOW_TAGS_DISABLED']}"
N8N_WORKFLOW_CALLER_POLICY_DEFAULT_OPTION="{env_vars['N8N_WORKFLOW_CALLER_POLICY_DEFAULT_OPTION']}"

# LICENSE
N8N_HIDE_USAGE_PAGE="{env_vars['N8N_HIDE_USAGE_PAGE']}"
N8N_LICENSE_ACTIVATION_KEY="{env_vars['N8N_LICENSE_ACTIVATION_KEY']}"
N8N_LICENSE_AUTO_RENEW_ENABLED="{env_vars['N8N_LICENSE_AUTO_RENEW_ENABLED']}"
N8N_LICENSE_AUTO_RENEW_OFFSET="{env_vars['N8N_LICENSE_AUTO_RENEW_OFFSET']}"
N8N_LICENSE_SERVER_URL="{env_vars['N8N_LICENSE_SERVER_URL']}"
HTTP_PROXY_LICENSE_SERVER="{env_vars['HTTP_PROXY_LICENSE_SERVER']}"
HTTPS_PROXY_LICENSE_SERVER="{env_vars['HTTPS_PROXY_LICENSE_SERVER']}"
"""

    # Process each line
    processed_lines = []
    for line in env_template.split('\n'):
        if '="None"' in line:
            # Comment out the line and remove the "None" value
            line = f"# {line.split('=')[0]}="
        processed_lines.append(line)

    env_vars = '\n'.join(processed_lines)


    docker_file_env_lines = []

    for line in env_template.split('\n'):
        if '="None"' in line:
            continue # dont add at all
        if '=""' in line:
            continue # dont add at all
        if line.startswith("#"):
            continue
        elif not '=' in line:
            continue
        elif 'N8N_VERSION' in line:
            continue
        docker_file_env_lines.append(f"      - {_replace_env_vars(line)}")



    dockercompose_vars = '\n'.join(docker_file_env_lines)
    


    return_map = {
        "env_vars": env_vars,
        "dockercompose_vars": dockercompose_vars
    }

    return return_map


def _create_dockercompose_file(dockercompose_vars, is_custom_image):

    dockercompose_file_start = """\
volumes:
  n8n_storage:
services:
  n8n:\
"""

    if is_custom_image:
        build_step = """\
    build:
      context: .
      args:
        N8N_VERSION: ${N8N_VERSION}\
"""
    else:
        build_step = "    image: docker.n8n.io/n8nio/n8n:${N8N_VERSION}"

    dockercompose_file_after_build = """\
    restart: unless-stopped
    environment:\
"""

    dockercompose_file_end = """\
    ports:
      - 5678:5678
    volumes:
      - n8n_storage:/home/node/.n8n\
"""

    dockercompose_file_list = [
        dockercompose_file_start,
        build_step,
        dockercompose_file_after_build,
        dockercompose_vars,
        dockercompose_file_end
    ]

    return '\n'.join(dockercompose_file_list)


def _create_dockerfile(list_of_packages: str):
    start_of_dockerfile = """\
# Base image from n8n's base image (which is based on Alpine)
FROM n8nio/base:18

# INSTALL EXTRA PACKAGES HERE using Apline package installer (APK)
#-------------------------------------------------------------------
RUN apk update
"""
# FFmpeg
# apk add --no-cache ffmpeg

    list_of_packages = [item.strip() for item in list_of_packages.split(',') if item.strip()]

    install_text = []

    for package in list_of_packages:
        if package == '':
            continue
        install_text.append(f"""\
# {package}
RUN apk add {package}
""")
        
    middle_of_dockerfile = "\n".join(install_text)


    end_of_dockerfile = """\
#-------------------------------------------------------------------


ARG N8N_VERSION

RUN if [ -z "$N8N_VERSION" ] ; then echo "The N8N_VERSION argument is missing!" ; exit 1; fi

ENV N8N_VERSION=${N8N_VERSION}
ENV NODE_ENV=production
ENV N8N_RELEASE_TYPE=stable
RUN set -eux; \
        npm install -g --omit=dev n8n@${N8N_VERSION} --ignore-scripts && \
        npm rebuild --prefix=/usr/local/lib/node_modules/n8n sqlite3 && \
        rm -rf /usr/local/lib/node_modules/n8n/node_modules/@n8n/chat && \
        rm -rf /usr/local/lib/node_modules/n8n/node_modules/n8n-design-system && \
        rm -rf /usr/local/lib/node_modules/n8n/node_modules/n8n-editor-ui/node_modules && \
        find /usr/local/lib/node_modules/n8n -type f -name "*.ts" -o -name "*.js.map" -o -name "*.vue" | xargs rm -f && \
        rm -rf /root/.npm

COPY docker-entrypoint.sh /

RUN \
        mkdir .n8n && \
        chown node:node .n8n
ENV SHELL /bin/sh
USER node
ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]
"""
    return start_of_dockerfile + middle_of_dockerfile + end_of_dockerfile


def _create_docker_entrypoint():
    docker_entrypoint = """
#!/bin/sh
if [ "$#" -gt 0 ]; then
  # Got started with arguments
  exec n8n "$@"
else
  # Got started without arguments
  exec n8n
fi
"""
    return docker_entrypoint


def _replace_env_vars(text):
    pattern = r'(\w+)="([^"]*)"'
    replacement = r'\1=${\1}'
    return re.sub(pattern, replacement, text)
