from docker import install_docker
from cloudflare import create_cf_tunnel
from n8n import start_n8n_container
from utils import env_vars, Question, Input_Type, timezones, local_timezone, Workflow_call_Policy, Database_Log_Level, Log_Level, Log_Location, Save_Modes, Reverse_Proxy_Type, Database_Options, Binary_Modes, Email_Modes
from utils import run_command


# INSTALL DOCKER (if needed) 
install_docker()
print("""
There is no undo functionality. If you enter a question wrong and submit it you must run the script again with the original command.

Reminder: You will have keys in a .env file on your system after this proccess. You are responsible to secure it.
""")


is_custom_image = False
list_of_packages = []


# ------------------------------------------------------------------------
# ------------------- FIRST SET OF REQUIRED QUESTIONS --------------------
# ------------------------------------------------------------------------

# Sets var for detailed setup type
detailed_setup = Question(
    "How customized would you like your n8n Install?:",
    Input_Type.CHOICE,
    None,
    ["Simple and Quick", "Detailed and Long"]
).answer == "Detailed and Long"


# Sets URL
domain = Question(
     "What's your domain?:",
     Input_Type.INPUT,
     ['N8N_EDITOR_BASE_URL', 'WEBHOOK_URL'],
     None,
     lambda selection: selection.count("/") == 0,
     "do not include 'https://' or any trailing '/'.",
     "https://"
).answer

Question(
    "What is your time zone?:",
    Input_Type.CHOICE,
    "GENERIC_TIMEZONE",
    timezones,
    default = str(local_timezone) or "America/New_York"
)

# \/ Jon let me know that the ai is disabled at the moment \/

# is_ai_enabled = Question(
#     "Would you like n8n AI enabled? If yes it will require an openAi API key (the AI in the n8n UI, not the AI nodes):",
#     Input_Type.CONFIRM,
#     None,
# ).answer == "True"

# AI Questions
# if is_ai_enabled:
#     env_vars["N8N_AI_ENABLED"] = "true"

#     Question(
#         "Enter your OpenAi API Key:",
#         Input_Type.PASSWORD,
#         "N8N_AI_OPENAI_API_KEY",
#     )

# ------------------------------------------------------------------------
# ----------------------- REVERSE PROXY QUESTIONS ------------------------
# ------------------------------------------------------------------------

reverse_proxy_option = Question(
    "How would you like to set up your domain?: (nginx potentially coming soon)",
    Input_Type.CHOICE,
    None,
    list(e.value for e in Reverse_Proxy_Type),
).answer

if reverse_proxy_option == Reverse_Proxy_Type.CLOUDFLARE.value:
    cloudflare_id = Question(
        "Cloudflare Account ID?:",
        Input_Type.INPUT,
        None,
    ).answer
    cloudflare_token = Question(
        "What's your CloudFlare Token? (must have Cloudflare Tunnel & DNS Scopes):",
        Input_Type.PASSWORD,
        None,
    ).answer


if detailed_setup:
    print("""
The following questions are the advanced setup options.

To skip an input question, just enter it empty.
For yes and no questions, yes will always be the default

Visit https://docs.n8n.io/hosting/configuration/environment-variables/ to see more details about each option
""")
    
    # -------------------------- Database questions --------------------------
    change_db = Question(
        "Would you like to keep the default database setup?",
        Input_Type.CONFIRM
    ).answer == "False"

    if change_db:
        db_type = Question(
            "Database Type",
            Input_Type.CHOICE,
            "DB_TYPE",
            list(e.value for e in Database_Options),
        ).answer
        Question(
            "Database Table Prefix",
            Input_Type.INPUT,
            "DB_TABLE_PREFIX"
        )

        if db_type == Database_Options.SQLITE.value:
            
            env_vars["DB_SQLITE_VACUUM_ON_STARTUP"] = Question(
            "Run vacuum on startup:",
            Input_Type.CONFIRM,
            ).answer.lower()
        else:
            print("\n I did not add postgres db options. Please go into the .env and docker-compose.yaml file after setup to manually configure postgres \n Feel free to add a PR adding this functionality")

    # -------------------------- DEPLOYMENT questions --------------------------

    env_vars["N8N_HIDE_USAGE_PAGE"] = str(
            Question(
                "Show the usage and plan page? (shown by default)",
                Input_Type.CONFIRM,
            ).answer == "False"
        ).lower()

    # Config file
    has_config_file = Question(
        "Continue without a JSON n8n config file?",
        Input_Type.CONFIRM,
    ).answer == "False"
    if has_config_file:
        Question(
            "Config File Path: (example: /<path-to-config>/my-config.json)",
            Input_Type.INPUT,
            "N8N_CONFIG_FILES"
        )
    
    # disable UI and Preview Mode questions
    env_vars["N8N_DISABLE_UI"] = str(Question(
            "Do you want a UI for n8n? (press n to disable the UI)",
            Input_Type.CONFIRM,
            ).answer == "False").lower() 
    env_vars["N8N_PREVIEW_MODE"] = str(Question(
            "Disable preview mode?: (press y for normal mode)",
            Input_Type.CONFIRM,
            ).answer == "False").lower()
    
    # Workflow templates
    env_vars["N8N_TEMPLATES_ENABLED"] = str(Question(
            "Disable workflow tempates?: (they are normally disabled by default)",
            Input_Type.CONFIRM,
            ).answer == "False").lower()
    
    # Workflow template host
    keep_default_template = Question(
        "Keep default template URL?: (Say no if you have your own template library)",
        Input_Type.CONFIRM,
    ).answer == "True"
    if not keep_default_template:
        Question(
            "URL of custom template host",
            Input_Type.INPUT,
            "N8N_TEMPLATES_HOST",
            )
    
    # Custom encryption key
    keep_default_encrpt = Question(
        "Do you want to keep the default n8n encryption key?:",
        Input_Type.CONFIRM,
    ).answer == "True"
    if not keep_default_encrpt:
        Question(
            "Custom encryption key",
            Input_Type.INPUT,
            "N8N_ENCRYPTION_KEY",
            )
    
        
    # custom graceful shutdown time
    keep_default_shut_down_time = Question(
        "Do you want to keep the default graceful shutdown timeout?:",
        Input_Type.CONFIRM,
    ).answer == "True"
    if not keep_default_shut_down_time:
        Question(
            "Input custom shutdown time in seconds:",
            Input_Type.INPUT,
            "N8N_GRACEFUL_SHUTDOWN_TIMEOUT",
            )
    
    # n8n api
    env_vars["N8N_PUBLIC_API_DISABLED"] = str(Question(
        "Enable the n8n API? (is enabled by default)",
        Input_Type.CONFIRM,
    ).answer == "False").lower()

    # hiring banner
    env_vars["N8N_HIRING_BANNER_ENABLED"] = Question(
        "Enable the n8n hiring banner?",
        Input_Type.CONFIRM,
    ).answer.lower()

    # -------------------------- BINARY DATA questions --------------------------

    # custom storage path
    keep_default_storage_path = Question(
        "Do you want to keep the default binary data storage path?:",
        Input_Type.CONFIRM,
    ).answer == "True"
    if not keep_default_storage_path:
        Question(
            "Input custom binary storage path:",
            Input_Type.INPUT,
            "N8N_BINARY_DATA_STORAGE_PATH",
        )
        
    env_vars["N8N_DEFAULT_BINARY_DATA_MODE"] = Binary_Modes( 
        Question(
            "Choose a binary mode:",
            Input_Type.CHOICE,
            None,
            list(e.value for e in Binary_Modes),
            default = Binary_Modes.default.value,
        ).answer
    ).name


    # -------------------------- EMAIL questions --------------------------

    email_mode = Email_Modes( 
        Question(
            "How would you like to set up email?",
            Input_Type.CHOICE,
            None,
            list(e.value for e in Email_Modes),
        ).answer
    )
    if email_mode == Email_Modes.SMTP:
        Question(
            "SMTP Host (server name)",
            Input_Type.INPUT,
            "N8N_SMTP_HOST"
        )
        Question(
            "SMTP Port",
            Input_Type.INPUT,
            "N8N_SMTP_PORT"
        )
        Question(
            "SMTP Password",
            Input_Type.PASSWORD,
            "N8N_SMTP_PASS"
        )
    if email_mode == Email_Modes.SERVICEACCOUNT:
        Question(
            "SMTP OAuth Service Client ID",
            Input_Type.INPUT,
            "N8N_SMTP_OAUTH_SERVICE_CLIENT"
        )
        Question(
            "SMTP OAuth private key",
            Input_Type.PASSWORD,
            "N8N_SMTP_OAUTH_PRIVATE_KEY"
        )
        Question(
            "Sender email address",
            Input_Type.INPUT,
            "N8N_SMTP_SENDER"
        )
    
    # 2fa
    env_vars["N8N_MFA_ENABLED"] = Question(
            "Enable two-factor authentication? (does not fource it, just allows it)",
            Input_Type.CONFIRM,
        ).answer.lower()
    
    # -------------------------- ENDPOINT questions --------------------------

    # Max payload size
    Question(
        "Max endpoint payload size (in MB)",
        Input_Type.INPUT,
        "N8N_PAYLOAD_SIZE_MAX",
        validate = lambda selection: not "," in selection,
        validate_message= "Please dont add commas",
        default = "16"
    )

   
    default_path_names = Question(
       "Do you want to keep default endpoint path names?",
       Input_Type.CONFIRM,
    ).answer == "True"
    
    if not default_path_names:
        Question(
            "Path used for webhook endpoint: (Example n8n.mylink.com/webhook/)",
            Input_Type.INPUT,
            "N8N_ENDPOINT_WEBHOOK",
            default = "webhook"
        )
        Question(
                "Path used for webhook test endpoint: (Example n8n.mylink.com/webhook-test/)",
                Input_Type.INPUT,
                "N8N_ENDPOINT_WEBHOOK_TEST",
                default = "webhook-test"
            )
        Question(
                "Path used for webhook waiting endpoint: (Example n8n.mylink.com/webhook-waiting/)",
                Input_Type.INPUT,
                "N8N_ENDPOINT_WEBHOOK_WAIT",
                default = "webhook-waiting"
            )
        
    
    # -------------------------- METRICS questions --------------------------
        
    keep_metrics_disabled = Question(
       "Do you want to keep n8n metrics disabled?",
       Input_Type.CONFIRM,
    ).answer == "True"
    
    if not keep_metrics_disabled:
        env_vars["N8N_METRICS"] = "true"

        Question(
                "n8n metrics prefix",
                Input_Type.INPUT,
                "N8N_METRICS_PREFIX",
                default = "n8n_"
            )
        env_vars["N8N_METRICS_INCLUDE_DEFAULT_METRICS"] = Question(
            "Include default metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
        env_vars["N8N_METRICS_INCLUDE_CACHE_METRICS"] = Question(
            "Include cache metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
        env_vars["N8N_METRICS_INCLUDE_MESSAGE_EVENT_BUS_METRICS"] = Question(
            "Include message event bus metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
        env_vars["N8N_METRICS_INCLUDE_WORKFLOW_ID_LABEL"] = Question(
            "Include workflow ID label in metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
        env_vars["N8N_METRICS_INCLUDE_NODE_TYPE_LABEL"] = Question(
            "Include node type label in metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
        env_vars["N8N_METRICS_INCLUDE_CREDENTIAL_TYPE_LABEL"] = Question(
            "Include credential type label in metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
        env_vars["N8N_METRICS_INCLUDE_API_ENDPOINTS"] = Question(
            "Include api endpoints in metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
        env_vars["N8N_METRICS_INCLUDE_API_PATH_LABEL"] = Question(
            "Include api path label in metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
        env_vars["N8N_METRICS_INCLUDE_API_METHOD_LABEL"] = Question(
            "Include api method label in metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
        env_vars["N8N_METRICS_INCLUDE_API_STATUS_CODE_LABEL"] = Question(
            "Include api status code label in metrics",
            Input_Type.CONFIRM,
        ).answer.lower()
    

    # -------------------------- EXTERNAL HOOKS questions --------------------------

    keep_external_hooks_disabled = Question(
       "Do you want to keep external hooks disabled?",
       Input_Type.CONFIRM,
    ).answer == "True"

    if not keep_external_hooks_disabled:
        Question(
            "External hooks files: (Files containing backend external hooks. Provide multiple files as a colon-separated list (:))",
            Input_Type.INPUT,
            "EXTERNAL_HOOK_FILES",
        )
        Question(
            "External front end hooks URLs: (URLs to files containing frontend external hooks. Provide multiple URLs as a colon-separated list (:))",
            Input_Type.INPUT,
            "EXTERNAL_FRONTEND_HOOKS_URLS",
        )
    
    # -------------------------- Executions questions --------------------------
    keep_default_timeout = Question(
       "Do you want to keep the default execution timeout? (no timeout by default)",
       Input_Type.CONFIRM,
    ).answer == "True"

    if not keep_default_timeout:
        Question(
            "Execution timeout in seconds (-1 to disable)",
            Input_Type.INPUT,
            "EXECUTIONS_TIMEOUT",
            validate = lambda selection: not "," in selection,
            validate_message= "Please dont add commas",
            default = "-1"
        )
    
    Question(
        "Max timeout users can set in the UI (in seconds)",
        Input_Type.INPUT,
        "EXECUTIONS_TIMEOUT_MAX",
        validate = lambda selection: not "," in selection,
        default = "3600"
    )

    env_vars["EXECUTIONS_DATA_SAVE_ON_ERROR"] =  Save_Modes(
        Question(
            "Save data on execution error?",
            Input_Type.CONFIRM,
        ).answer
    ).name

    env_vars["EXECUTIONS_DATA_SAVE_ON_SUCCESS"] = Save_Modes(
        Question(
            "Save data on execution success?",
            Input_Type.CONFIRM,
        ).answer
    ).name

    
    env_vars["EXECUTIONS_DATA_SAVE_ON_PROGRESS"] = str(
        Question(
            "Disable save data on execution progress? (disabled by default)",
            Input_Type.CONFIRM,
        ).answer == "False"
    ).lower()

    env_vars["EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS"] = Question(
        "Save data on manual executions?",
        Input_Type.CONFIRM,
    ).answer.lower()

    env_vars["EXECUTIONS_DATA_PRUNE"] = Question(
        "Delete old execution data (prune) (past the max age)?",
        Input_Type.CONFIRM,
    ).answer.lower()

    Question(
        "Execution data max age in hours",
        Input_Type.INPUT,
        "EXECUTIONS_DATA_MAX_AGE",
        validate = lambda selection: not "," in selection,
        validate_message= "Please dont add commas",
        default = "336"
    )

    Question(
        "Maximum number of executions to keep in the database (enter 0 for unlimited)",
        Input_Type.INPUT,
        "EXECUTIONS_DATA_PRUNE_MAX_COUNT",
        validate = lambda selection: not "," in selection,
        validate_message= "Please dont add commas",
        default = "10000"
    )

    Question(
        "How old (hours) the finished execution data has to be to get hard-deleted",
        Input_Type.INPUT,
        "EXECUTIONS_DATA_HARD_DELETE_BUFFER",
        validate = lambda selection: not "," in selection,
        validate_message= "Please dont add commas",
        default = "1"
    )

    Question(
        "How often (minutes) execution data should be hard-deleted",
        Input_Type.INPUT,
        "EXECUTIONS_DATA_PRUNE_HARD_DELETE_INTERVAL",
        validate = lambda selection: not "," in selection,
        validate_message= "Please dont add commas",
        default = "15"
    )

    Question(
        "How often (minutes) execution data should be soft-deleted",
        Input_Type.INPUT,
        "EXECUTIONS_DATA_PRUNE_SOFT_DELETE_INTERVAL",
        validate = lambda selection: not "," in selection,
        validate_message= "Please dont add commas",
        default = "60"
    )

    Question(
        "Max production executions allowed to run concurrently. Add -1 for no limit",
        Input_Type.INPUT,
        "N8N_CONCURRENCY_PRODUCTION_LIMIT",
        validate = lambda selection: not "," in selection,
        validate_message= "Please dont add commas",
        default = "-1"
    )

    # -------------------------- LOG questions --------------------------
    keep_default_log = Question(
       "Do you want to keep the default log settings",
       Input_Type.CONFIRM,
    ).answer == "True"

    if not keep_default_log:
        Question(
            "Log output level",
            Input_Type.CHOICE,
            "N8N_LOG_LEVEL",
            list(e.name for e in Log_Level),            
        )
        log_location = Question(
            "Log output location",
            Input_Type.CHOICE,
            "N8N_LOG_OUTPUT",
            list(e.name for e in Log_Location),            
        ).answer

        if log_location == Log_Location.file.name:
            Question(
                "Max log file count",
                Input_Type.INPUT,
                "N8N_LOG_FILE_COUNT_MAX",
                validate = lambda selection: not "," in selection,
                validate_message = "Please dont add commas",
                default = "100"
            )
            Question(
                "Max log file size (in MB)",
                Input_Type.INPUT,
                "N8N_LOG_FILE_SIZE_MAX",
                validate = lambda selection: not "," in selection,
                validate_message = "Please dont add commas",
                default = "16"
            )
            Question(
                "Log file path",
                Input_Type.INPUT,
                "N8N_LOG_FILE_LOCATION",
                default = "n8n/logs/n8n.log"
            )
        
        env_vars["DB_LOGGING_ENABLED"] = str(
            Question(
                "Disable database logging? (disabled by default)",
                Input_Type.CONFIRM,
            ).answer == "False"
        ).lower()

        if env_vars["DB_LOGGING_ENABLED"] == "true":
            Question(
                "Database log level (For all logs select all)",
                Input_Type.CHOICE,
                "DB_LOGGING_OPTIONS",
                list(e.name for e in Database_Log_Level),            
            ).answer
            Question(
                "Maximum execution time (in milliseconds) before n8n logs a warning. (Set to 0 to disable)",
                Input_Type.INPUT,
                "DB_LOGGING_MAX_EXECUTION_TIME",
                validate = lambda selection: not "," in selection,
                validate_message = "Please dont add commas",
                default = "1000"
            )
        
        env_vars["CODE_ENABLE_STDOUT"] = str(
            Question(
                "Disable code node logging? (disabled by default)",
                Input_Type.CONFIRM,
            ).answer == "False"
        ).lower()

        # -------------------------- LOG STREAMING questions --------------------------

        keep_default_log = Question(
            "Keep log streaming settings at defaults? (Only available for enterprise)",
            Input_Type.CONFIRM,
        ).answer == "True"

        if not keep_default_log:
            Question(
                "How often (in milliseconds) to check for unsent event messages. Can in rare cases send message twice. (Set to 0 to disable)",
                Input_Type.INPUT,
                "N8N_EVENTBUS_CHECKUNSENTINTERVAL",
                validate = lambda selection: not "," in selection,
                validate_message = "Please dont add commas",
                default = "0"
            )
            env_vars["N8N_EVENTBUS_LOGWRITER_SYNCFILEACCESS"] = str(
                Question(
                    "Disable all file access happening synchronously within the thread? (disabled by default)",
                    Input_Type.CONFIRM,
                ).answer == "False"
            ).lower()
            Question(
                "Number of event log files to keep",
                Input_Type.INPUT,
                "N8N_EVENTBUS_LOGWRITER_KEEPLOGCOUNT",
                validate = lambda selection: not "," in selection,
                validate_message = "Please dont add commas",
                default = "3"
            )
            Question(
                "Maximum size (in KB) of an event log file before a new one starts:",
                Input_Type.INPUT,
                "N8N_EVENTBUS_LOGWRITER_MAXFILESIZEINKB",
                validate = lambda selection: not "," in selection,
                validate_message = "Please dont add commas",
                default = "10240"
            )
            Question(
                "Basename of the event log file:",
                Input_Type.INPUT,
                "N8N_EVENTBUS_LOGWRITER_LOGBASENAME",
                default = "n8nEventLog"
            )
    

    # -------------------------- External data storage questions --------------------------

    keep_external_data_disabled = Question(
        "Disable external data storage (disabled by default)",
        Input_Type.CONFIRM,
    ).answer == "True"

    if not keep_external_data_disabled:
        Question(
            "Host of the n8n bucket in S3-compatible external storage. For example, s3.us-east-1.amazonaws.com:",
            Input_Type.INPUT,
            "N8N_EXTERNAL_STORAGE_S3_HOST",
        )
        Question(
            "Name of the n8n bucket in S3-compatible external storage:",
            Input_Type.INPUT,
            "N8N_EXTERNAL_STORAGE_S3_BUCKET_NAME",
        )
        Question(
            "Region of the n8n bucket in S3-compatible external storage. For example, us-east-1",
            Input_Type.INPUT,
            "N8N_EXTERNAL_STORAGE_S3_BUCKET_REGION",
        )
        Question(
            "Access key in S3-compatible external storage",
            Input_Type.INPUT,
            "N8N_EXTERNAL_STORAGE_S3_ACCESS_KEY",
        )
        Question(
            "Access secret in S3-compatible external storage",
            Input_Type.PASSWORD,
            "N8N_EXTERNAL_STORAGE_S3_ACCESS_SECRET",
        )

    # -------------------------- NODE questions --------------------------
    
    block_js_modules = Question(
        "Disable JS modules in the code node? (disabled by default)",
        Input_Type.CONFIRM,
    ).answer == "False"

    if block_js_modules:
        Question(
            "Comma seperated list of built in modules to allow (meaning modules already in n8n) (use '*' for all)",
            Input_Type.INPUT,
            "NODE_FUNCTION_ALLOW_BUILTIN",
            default= "*"
        )
        Question(
            "Permit users to import specific external modules (from n8n/node_modules) in the Code node. n8n disables importing modules by default",
            Input_Type.INPUT,
            "NODE_FUNCTION_ALLOW_EXTERNAL",
            default= "*"
        )
    
    keep_default_error_node = Question(
        "Keep default error trigger node?",
        Input_Type.CONFIRM,
    )

    if not keep_default_error_node:
        Question(
            "Specify which node type to use as Error Trigger",
            Input_Type.INPUT,
            "NODES_ERROR_TRIGGER_TYPE",
            default= "n8n-nodes-base.errorTrigger"
        )

    env_vars["N8N_COMMUNITY_PACKAGES_ENABLED"] = Question(
            "Enable community nodes?",
            Input_Type.CONFIRM,
        ).answer.lower()

    # -------------------------- queue mode questions --------------------------

    keep_queue_mode_disabled = Question(
       "Do you want to keep queue mode disabled? (enter yes if you don't know what queue mode is)",
       Input_Type.CONFIRM,
    ).answer == "True"

    if not keep_queue_mode_disabled:
        print(" i have not made this yes because i want to do it right. Let me know if you want it! For now please configure this manually, i have the queue mode env vars commented out in there already.")

    # -------------------------- Security questions --------------------------

    keep_security_default = Question(
        "Keep security settings default?",
        Input_Type.CONFIRM,
    ).answer == "True"

    if not keep_security_default:
        env_vars["N8N_BLOCK_ENV_ACCESS_IN_NODE"] = str(
            Question(
                "Block users ability to access environment variables in expressions and the Code node (blocked by default)",
                Input_Type.CONFIRM,
            ).answer == "False"
        ).lower()

        Question(
            "Limits access to files in these directories. Provide multiple files as a colon-separated list (':') (leave blank to skip)",
            Input_Type.INPUT,
            "N8N_RESTRICT_FILE_ACCESS_TO",
        )
        env_vars["N8N_BLOCK_FILE_ACCESS_TO_N8N_FILES"] = Question(
                "Block access to all files in the .n8n directory and user defined configuration files (blocked by default)",
                Input_Type.CONFIRM,
            ).answer.lower()
        Question(
            "Number of days to consider a workflow abandoned if it's not executed",
            Input_Type.INPUT,
            "N8N_SECURITY_AUDIT_DAYS_ABANDONED_WORKFLOW",
            validate = lambda selection: not "," in selection,
            validate_message = "Please dont add commas",
            default = "90"
        )
        env_vars["N8N_SECURE_COOKIE"] = Question(
                "Require SSL to access n8n",
                Input_Type.CONFIRM,
            ).answer.lower()
        
    # -------------------------- workflow questions --------------------------
    Question(
            "The default name used for new workflows:",
            Input_Type.INPUT,
            "WORKFLOWS_DEFAULT_NAME",
            default = "My workflow"
        )
    env_vars["N8N_ONBOARDING_FLOW_DISABLED"] = str(
            Question(
                "Enable the onboarding tips when creating a new workflow",
                Input_Type.CONFIRM,
            ).answer == "False"
        ).lower()
    env_vars["N8N_WORKFLOW_TAGS_DISABLED"] = str(
            Question(
                "Enable tags for organizing workflows",
                Input_Type.CONFIRM,
            ).answer == "False"
        ).lower()
    

    # -------------------------- License questions --------------------------
    is_enterprise = Question(
        "Do you have an enterprise key?",
        Input_Type.CONFIRM,
    ).answer == "True"

    if is_enterprise:
        Question(
            "Enterprise activation key:",
            Input_Type.INPUT,
            "N8N_LICENSE_ACTIVATION_KEY",
        )

        Question(
            "Which workflows can call another workflow:",
            Input_Type.CHOICE,
            "N8N_WORKFLOW_CALLER_POLICY_DEFAULT_OPTION",
            list(e.name for e in Workflow_call_Policy),
        )
        Question(
            "How often (in seconds) to check for secret updates",
            Input_Type.INPUT,
            "N8N_EXTERNAL_SECRETS_UPDATE_INTERVAL",
            validate = lambda selection: not "," in selection,
            validate_message = "Please dont add commas",
            default = "300"
        )
    
#     is_custom_image = Question(
#         "Continue with default image? A custom image would be for extra dependencies like ffmpeg. This adds a build step which takes much longer than using the prebuilt image. (Y = default image)",
#         Input_Type.CONFIRM,
#     ).answer == "False"

    
#     if is_custom_image:
#         list_of_packages = Question(
#             "Comma seperated list of required extra dependencies:",
#             Input_Type.INPUT,
#         ).answer
#         print("""
# This will make a docker file in the root of the n8n directory.
              
# If you need to modify it further then go there and make and changes then run `docker compose build` in the same directory.
# From there you will need to restart the container with `docker compose down` and `docker compose up -d`
# """)


# Dont forget to ask stuff about custom image and custom dependencies



print("\nstarting n8n...")
start_n8n_container(env_vars, is_custom_image, list_of_packages)
print("n8n started")


# Start cloudflare tunnel (if selected)
if reverse_proxy_option == Reverse_Proxy_Type.CLOUDFLARE.value:
    create_cf_tunnel(domain, cloudflare_id, cloudflare_token)



print("""
Thank you for using my tool!
Please give me feedback if you have any!
      
liam@teraprise.io
""")

# TODO: add cleanup scripts here
print("deleting temp folder...")
run_command("rm -rf n8n-auto-install")
