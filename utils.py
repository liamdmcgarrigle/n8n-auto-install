import subprocess
from typing import List, Optional, Callable
from enum import Enum, auto
from InquirerPy import prompt
from InquirerPy import inquirer
from tzlocal import get_localzone


local_timezone = get_localzone()

def run_command(command: str):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Exit code: {e.returncode}")
        print(f"Output: {e.output}")
        print(f"Error: {e.stderr}")
        exit(1)
    
def create_file(path, content):
    f = open(path, "x")
    f.write(content)
    f.close()

class Reverse_Proxy_Type(Enum):
    CLOUDFLARE = "Cloudflare Tunnel (best for beginners and dynamic IP)"
    # NGNIX = "NGNIX (best for experienced techs with dedicated IP)"
    NON = "Nothing (Will not be able to access n8n outside of your own network)"

class Database_Options(Enum):
    SQLITE = "sqlite"
    POSTGRESDB = "postgresdb"

class Binary_Modes(Enum):
    default = "memory (default)"
    filesystem = "filesystem (not available for enterprise)"
    s3 = "s3 remote storage"

class Email_Modes(Enum):
    Non = "No email configuration (Email password resets and user invites will not work)"
    SMTP = "Manual SMTP configuration"
    SERVICEACCOUNT = "Service account"

class Save_Modes(Enum):
    all = "True"
    none = "False"

class Workflow_call_Policy(Enum):
    workflowsFromSameOwner = auto()
    any = auto()
    none = auto()

class Log_Level(Enum):
    info = auto()
    warn = auto()
    error = auto()
    verbose = auto()
    debug = auto()

class Database_Log_Level(Enum):
    query = auto()
    error = auto()
    schema = auto()
    warn = auto()
    info = auto()
    log = auto()
    all = auto()

class Log_Location(Enum):
    console = auto()
    file = auto()


class Input_Type(Enum):
    """
    Enum defining types of input for Question class.

    Attributes:
        INPUT: Free-form text input.
        CHOICE: Multiple-choice input.
        CONFIRM: Yes/No confirmation.
        PASSWORD: Masked input for sensitive information.
    """
    INPUT = auto()
    CHOICE = auto()
    CONFIRM = auto()
    PASSWORD = auto()


class Question:
    """
    A class to create interactive prompts, collect user responses, and update environment variables.

    The class prompts the user with the question on instantiation. See examples below.

    This class handles various types of user inputs, including free-form text, multiple choice,
    confirmations, and password entries. It can automatically update specified environment
    variables with the user's response or be used to get the answer of the question.

    Attributes:
        question (str): The text of the question to be asked.
        input_type (Input_Type): The type of input expected from the user.
        env_to_update (List[str] | None): Environment variables to update with the answer.
        options (List[str] | None): List of options for multiple-choice questions.
        validate (Callable | None): Optional function to validate user input.
        validate_message (str | None): Error message to display if validation fails.
        env_var_prefix (str): Prefix to add to the answer when updating environment variables.
        default (str | None): Default value for the question.
        answer (str): The user's answer after prompting.

    Methods:
        `_prompt_question()`: Internal method to handle the actual prompting based on input type.
        `_prep_list_of_env_vars(env_to_update)`: Prepares the list of environment variables to update.
        
    Examples:
        Multiple choice question:
        >>> install_complexity = Question(
        ...     "How customized would you like your n8n Install?:",
        ...     Input_Type.CHOICE,
        ...     options=['simple', 'complex']
        ... )
        This creates a multiple-choice question without updating any environment variables.

        Password input:
        >>> open_ai_key = Question(
        ...     "Enter your OpenAi API Key:",
        ...     Input_Type.PASSWORD,
        ...     env_to_update="N8N_AI_OPENAI_API_KEY"
        ... )
        This prompts for a password and updates the "N8N_AI_OPENAI_API_KEY" environment variable.

        Text input with validation:
        >>> domain_name = Question(
        ...     "What's your domain?:",
        ...     Input_Type.INPUT,
        ...     env_to_update=['N8N_EDITOR_BASE_URL', 'WEBHOOK_URL'],
        ...     validate=lambda selection: selection.count("/") == 0,
        ...     validate_message="do not include 'https://' or any trailing '/'.",
        ...     env_var_prefix="https://"
        ... )
        This creates a text input question that updates two environment variables with 'https://'
        prefixed to the user's input. It includes input validation to ensure the domain doesn't
        contain slashes. The prefix is only added to the env var and the answer prop on the class 
        remains without the prefix.

        Confirmation question:
        >>> enterprise_customer = Question(
        ...     "Do you have an enterprise key?:",
        ...     Input_Type.CONFIRM
        ... ).answer
        >>> if enterprise_customer == 'True':
        ...     # Ask for enterprise key here
        This creates a yes/no question and immediately retrieves the answer for conditional logic.

    Note:
        The question is automatically prompted upon initialization, and the answer
        is stored in the `answer` attribute. Environment variables are updated automatically
        if `env_to_update` is provided. If no validation function is provided for Input_Type.INPUT,
        a default validation is applied to prevent answers with only spaces.
    """
    def __init__(
            self, 
            question: str, 
            input_type: Input_Type, 
            env_to_update: str | List[str] | None = None, 
            options: Optional[List[str]] = None, 
            validate: Optional[Callable] = None, 
            validate_message: Optional[str] = None, 
            env_var_prefix: Optional[str] = "",
            default: Optional[str] = None,):
        self.question: str = question
        self.input_type: Input_Type = input_type
        self.validate: Callable | None = validate
        self.validate_message: str | None = validate_message
        self.env_var_prefix: str = env_var_prefix
        self.default = default
        self.options = options
        self.env_to_update: List[str] | None = self._prep_list_of_env_vars(env_to_update)
        self.answer: str = self._promt_question()

    def _promt_question(self) -> str:
        # implimentation of asking the question
        if self.input_type == Input_Type.INPUT:
            question = [
                {
                    "type": "input",
                    "message": self.question,
                    "validate": self.validate or (lambda selection: selection != " "),
                    "invalid_message": self.validate_message or "If you want to skip the question, enter a blank value (you currently have a space)",
                    "default": self.default or "",
                    "name": "current_question",
                }
            ]
        elif self.input_type == Input_Type.CHOICE:
            question = [
                {
                    "type": "list",
                    "message": self.question,
                    "choices": self.options,
                    "default": self.default or "",
                    "name": "current_question",
                }
            ]
        elif self.input_type == Input_Type.CONFIRM:
            question = [
                {
                    "type": "confirm",
                    "message": self.question,
                    "default": True,
                    "name": "current_question",
                }
            ]
        elif self.input_type == Input_Type.PASSWORD:
            question = [
                {
                    "type": "password",
                    "message": self.question,
                    "name": "current_question",
                }
            ]
        
        answer = prompt(question)

        # Updates each entirement Var to the answer. Will do a single one, a list, or none
        if self.env_to_update != None:  
            for env_var in self.env_to_update:
                env_vars[env_var] = self.env_var_prefix + answer["current_question"]

        
        return str(answer["current_question"])
    
    def _prep_list_of_env_vars(self, env_to_update) -> List[str] | None:
        if type(env_to_update) == str:
            return [env_to_update]
        elif env_to_update == None:
            return None
        else:
            return env_to_update


env_vars = {

    # AI VARIABLES
    # "N8N_AI_ENABLED": None,
    # "N8N_AI_PROVIDER": "openai",
    # "N8N_AI_OPENAI_API_KEY": None,

    # CREDENTIALS VARIABLES
    "CREDENTIALS_DEFAULT_NAME": "My credentials",

    # DATABASE VARIABLES
    "DB_TYPE": "sqlite",
    "DB_TABLE_PREFIX": None,
    "DB_SQLITE_VACUUM_ON_STARTUP": "false",

    # DEPLOYMENT VARIABLES
    "N8N_EDITOR_BASE_URL": None,
    "N8N_PERSONALIZATION_ENABLED": "false",
    "N8N_CONFIG_FILES": None,
    "N8N_DISABLE_UI": None,
    "N8N_PREVIEW_MODE": None,
    "N8N_TEMPLATES_ENABLED": "false",
    "N8N_TEMPLATES_HOST": None,
    "N8N_ENCRYPTION_KEY": None,
    "N8N_GRACEFUL_SHUTDOWN_TIMEOUT": "30",
    "N8N_PUBLIC_API_DISABLED": None,
    "N8N_HIRING_BANNER_ENABLED": None,

    # BINARY DATA 
    "N8N_AVAILABLE_BINARY_DATA_MODES": None,
    "N8N_BINARY_DATA_STORAGE_PATH": None,
    "N8N_DEFAULT_BINARY_DATA_MODE": None,

    # USER MANANEMENT 
    #  SMTP EMAIL
    "N8N_EMAIL_MODE": "smtp",
    "N8N_SMTP_HOST": None,
    "N8N_SMTP_PORT": None,
    "N8N_SMTP_USER": None,
    "N8N_SMTP_PASS": None,
    #  SERVICE ACCOUNT EMAIL
    "N8N_SMTP_OAUTH_SERVICE_CLIENT": None,
    "N8N_SMTP_OAUTH_PRIVATE_KEY": None,
    "N8N_SMTP_SENDER": None,
    "N8N_SMTP_SSL": "true",
    #  Templates
    "N8N_UM_EMAIL_TEMPLATES_INVITE": None,
    "N8N_UM_EMAIL_TEMPLATES_PWRESET": None,
    "N8N_UM_EMAIL_TEMPLATES_WORKFLOW_SHARED": None,
    "N8N_UM_EMAIL_TEMPLATES_CREDENTIALS_SHARED": None,
    #  Token options
    "N8N_USER_MANAGEMENT_JWT_SECRET": None,
    "N8N_USER_MANAGEMENT_JWT_DURATION_HOURS": None,
    "N8N_USER_MANAGEMENT_JWT_REFRESH_TIMEOUT_HOURS": None,
    "N8N_MFA_ENABLED": None,

    # ENDPOINTS
    "N8N_PAYLOAD_SIZE_MAX": "16",
    "N8N_METRICS": "false",
    "N8N_METRICS_PREFIX": "n8n_",
    "N8N_METRICS_INCLUDE_DEFAULT_METRICS": "true",
    "N8N_METRICS_INCLUDE_CACHE_METRICS": "false",
    "N8N_METRICS_INCLUDE_MESSAGE_EVENT_BUS_METRICS": "false",
    "N8N_METRICS_INCLUDE_WORKFLOW_ID_LABEL": "false",
    "N8N_METRICS_INCLUDE_NODE_TYPE_LABEL": "false",
    "N8N_METRICS_INCLUDE_CREDENTIAL_TYPE_LABEL": "false",
    "N8N_METRICS_INCLUDE_API_ENDPOINTS": "false",
    "N8N_METRICS_INCLUDE_API_PATH_LABEL": "false",
    "N8N_METRICS_INCLUDE_API_METHOD_LABEL": "false",
    "N8N_METRICS_INCLUDE_API_STATUS_CODE_LABEL": "false",
    "N8N_ENDPOINT_REST": "rest",
    "N8N_ENDPOINT_WEBHOOK": "webhook",
    "N8N_ENDPOINT_WEBHOOK_TEST": "webhook-test",
    "N8N_ENDPOINT_WEBHOOK_WAIT": "webhook-waiting",
    "WEBHOOK_URL": None,
    "N8N_DISABLE_PRODUCTION_MAIN_PROCESS": "false",

    # EXTERNAL HOOKS
    "EXTERNAL_HOOK_FILES": None,
    "EXTERNAL_FRONTEND_HOOKS_URLS": None,

    # EXECUTION
    "EXECUTIONS_MODE": "regular",
    "EXECUTIONS_TIMEOUT": "-1",
    "EXECUTIONS_TIMEOUT_MAX": "3600",
    "EXECUTIONS_DATA_SAVE_ON_ERROR": "all",
    "EXECUTIONS_DATA_SAVE_ON_SUCCESS": "all",
    "EXECUTIONS_DATA_SAVE_ON_PROGRESS": "false",
    "EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS": "true",
    "EXECUTIONS_DATA_PRUNE": "true",
    "EXECUTIONS_DATA_MAX_AGE": "336",
    "EXECUTIONS_DATA_PRUNE_MAX_COUNT": "10000",
    "EXECUTIONS_DATA_HARD_DELETE_BUFFER": "1",
    "EXECUTIONS_DATA_PRUNE_HARD_DELETE_INTERVAL": "15",
    "EXECUTIONS_DATA_PRUNE_SOFT_DELETE_INTERVAL": "60",
    "N8N_CONCURRENCY_PRODUCTION_LIMIT": "-1",
    
    # LOGS
    "N8N_LOG_LEVEL": "info",
    "N8N_LOG_OUTPUT": "console",
    "N8N_LOG_FILE_COUNT_MAX": None,
    "N8N_LOG_FILE_SIZE_MAX": None,
    "N8N_LOG_FILE_LOCATION": None,
    "DB_LOGGING_ENABLED": "false",
    "DB_LOGGING_OPTIONS": None,
    "DB_LOGGING_MAX_EXECUTION_TIME": None,
    "CODE_ENABLE_STDOUT": "false",

    # LOG STREAMING
    "N8N_EVENTBUS_CHECKUNSENTINTERVAL": "0",
    "N8N_EVENTBUS_LOGWRITER_SYNCFILEACCESS": "false",
    "N8N_EVENTBUS_LOGWRITER_KEEPLOGCOUNT": "3",
    "N8N_EVENTBUS_LOGWRITER_MAXFILESIZEINKB": "10240",
    "N8N_EVENTBUS_LOGWRITER_LOGBASENAME": "n8nEventLog",

    # EXTERNAL DATA STORAGE
    "N8N_EXTERNAL_STORAGE_S3_HOST": None,
    "N8N_EXTERNAL_STORAGE_S3_BUCKET_NAME": None,
    "N8N_EXTERNAL_STORAGE_S3_BUCKET_REGION": None,
    "N8N_EXTERNAL_STORAGE_S3_ACCESS_KEY": None,
    "N8N_EXTERNAL_STORAGE_S3_ACCESS_SECRET": None,

    # NODES
    "NODES_INCLUDE": None,
    "NODES_EXCLUDE": None,
    "NODE_FUNCTION_ALLOW_BUILTIN": None,
    "NODE_FUNCTION_ALLOW_EXTERNAL": None,
    "NODES_ERROR_TRIGGER_TYPE": "n8n-nodes-base.errorTrigger",
    "N8N_CUSTOM_EXTENSIONS": None,
    "N8N_COMMUNITY_PACKAGES_ENABLED": "true",
    "N8N_COMMUNITY_PACKAGES_REGISTRY": "https://registry.npmjs.org",

    # QUEUE MODE
    "QUEUE_BULL_PREFIX": None,
    "QUEUE_BULL_REDIS_DB": None,
    "QUEUE_BULL_REDIS_HOST": "localhost",
    "QUEUE_BULL_REDIS_PORT": "6379",
    "QUEUE_BULL_REDIS_USERNAME": None,
    "QUEUE_BULL_REDIS_PASSWORD": None,
    "QUEUE_BULL_REDIS_TIMEOUT_THRESHOLD": "1000",
    "QUEUE_BULL_REDIS_CLUSTER_NODES": None,
    "QUEUE_BULL_REDIS_TLS": None,
    "QUEUE_RECOVERY_INTERVAL": None,
    "QUEUE_HEALTH_CHECK_ACTIVE": "false",
    "QUEUE_HEALTH_CHECK_PORT": None,
    "QUEUE_WORKER_LOCK_DURATION": "30000",
    "QUEUE_WORKER_LOCK_RENEW_TIME": "15000",
    "QUEUE_WORKER_STALLED_INTERVAL": "30000",
    "QUEUE_WORKER_MAX_STALLED_COUNT": "1",

    # SECURITY
    "N8N_BLOCK_ENV_ACCESS_IN_NODE": "false",
    "N8N_RESTRICT_FILE_ACCESS_TO": None,
    "N8N_BLOCK_FILE_ACCESS_TO_N8N_FILES": "true",
    "N8N_SECURITY_AUDIT_DAYS_ABANDONED_WORKFLOW": "90",
    "N8N_SECURE_COOKIE": "true",

    # GIT
    "N8N_SOURCECONTROL_DEFAULT_SSH_KEY_TYPE": "ed25519",

    # EXTERNAL SECRETS
    "N8N_EXTERNAL_SECRETS_UPDATE_INTERVAL": None,

    # LOCAL
    "GENERIC_TIMEZONE": None,
    "N8N_DEFAULT_LOCALE": None,

    # WORKFLOWS
    "WORKFLOWS_DEFAULT_NAME": "My workflow",
    "N8N_ONBOARDING_FLOW_DISABLED": "false",
    "N8N_WORKFLOW_TAGS_DISABLED": "false",
    "N8N_WORKFLOW_CALLER_POLICY_DEFAULT_OPTION": "workflowsFromSameOwner",

    # LICENSE
    "N8N_HIDE_USAGE_PAGE": "false",
    "N8N_LICENSE_ACTIVATION_KEY": None,
    "N8N_LICENSE_AUTO_RENEW_ENABLED": "true",
    "N8N_LICENSE_AUTO_RENEW_OFFSET": None,
    "N8N_LICENSE_SERVER_URL": None,
    "HTTP_PROXY_LICENSE_SERVER": None,
    "HTTPS_PROXY_LICENSE_SERVER": None,
    }

timezones = [
    "Africa/Abidjan",
    "Africa/Algiers",
    "Africa/Bissau",
    "Africa/Cairo",
    "Africa/Casablanca",
    "Africa/Ceuta",
    "Africa/El_Aaiun",
    "Africa/Johannesburg",
    "Africa/Juba",
    "Africa/Khartoum",
    "Africa/Lagos",
    "Africa/Maputo",
    "Africa/Monrovia",
    "Africa/Nairobi",
    "Africa/Ndjamena",
    "Africa/Sao_Tome",
    "Africa/Tripoli",
    "Africa/Tunis",
    "Africa/Windhoek",
    "America/Adak",
    "America/Anchorage",
    "America/Araguaina",
    "America/Argentina/Buenos_Aires",
    "America/Argentina/Catamarca",
    "America/Argentina/Cordoba",
    "America/Argentina/Jujuy",
    "America/Argentina/La_Rioja",
    "America/Argentina/Mendoza",
    "America/Argentina/Rio_Gallegos",
    "America/Argentina/Salta",
    "America/Argentina/San_Juan",
    "America/Argentina/San_Luis",
    "America/Argentina/Tucuman",
    "America/Argentina/Ushuaia",
    "America/Asuncion",
    "America/Bahia",
    "America/Bahia_Banderas",
    "America/Barbados",
    "America/Belem",
    "America/Belize",
    "America/Boa_Vista",
    "America/Bogota",
    "America/Boise",
    "America/Cambridge_Bay",
    "America/Campo_Grande",
    "America/Cancun",
    "America/Caracas",
    "America/Cayenne",
    "America/Chicago",
    "America/Chihuahua",
    "America/Ciudad_Juarez",
    "America/Costa_Rica",
    "America/Cuiaba",
    "America/Danmarkshavn",
    "America/Dawson",
    "America/Dawson_Creek",
    "America/Denver",
    "America/Detroit",
    "America/Edmonton",
    "America/Eirunepe",
    "America/El_Salvador",
    "America/Fort_Nelson",
    "America/Fortaleza",
    "America/Glace_Bay",
    "America/Goose_Bay",
    "America/Grand_Turk",
    "America/Guatemala",
    "America/Guayaquil",
    "America/Guyana",
    "America/Halifax",
    "America/Havana",
    "America/Hermosillo",
    "America/Indiana/Indianapolis",
    "America/Indiana/Knox",
    "America/Indiana/Marengo",
    "America/Indiana/Petersburg",
    "America/Indiana/Tell_City",
    "America/Indiana/Vevay",
    "America/Indiana/Vincennes",
    "America/Indiana/Winamac",
    "America/Inuvik",
    "America/Iqaluit",
    "America/Jamaica",
    "America/Juneau",
    "America/Kentucky/Louisville",
    "America/Kentucky/Monticello",
    "America/La_Paz",
    "America/Lima",
    "America/Los_Angeles",
    "America/Maceio",
    "America/Managua",
    "America/Manaus",
    "America/Martinique",
    "America/Matamoros",
    "America/Mazatlan",
    "America/Menominee",
    "America/Merida",
    "America/Metlakatla",
    "America/Mexico_City",
    "America/Miquelon",
    "America/Moncton",
    "America/Monterrey",
    "America/Montevideo",
    "America/New_York",
    "America/Nome",
    "America/Noronha",
    "America/North_Dakota/Beulah",
    "America/North_Dakota/Center",
    "America/North_Dakota/New_Salem",
    "America/Nuuk",
    "America/Ojinaga",
    "America/Panama",
    "America/Paramaribo",
    "America/Phoenix",
    "America/Port-au-Prince",
    "America/Porto_Velho",
    "America/Puerto_Rico",
    "America/Punta_Arenas",
    "America/Rankin_Inlet",
    "America/Recife",
    "America/Regina",
    "America/Resolute",
    "America/Rio_Branco",
    "America/Santarem",
    "America/Santiago",
    "America/Santo_Domingo",
    "America/Sao_Paulo",
    "America/Scoresbysund",
    "America/Sitka",
    "America/St_Johns",
    "America/Swift_Current",
    "America/Tegucigalpa",
    "America/Thule",
    "America/Tijuana",
    "America/Toronto",
    "America/Vancouver",
    "America/Whitehorse",
    "America/Winnipeg",
    "America/Yakutat",
    "Antarctica/Casey",
    "Antarctica/Davis",
    "Antarctica/Macquarie",
    "Antarctica/Mawson",
    "Antarctica/Palmer",
    "Antarctica/Rothera",
    "Antarctica/Troll",
    "Antarctica/Vostok",
    "Asia/Almaty",
    "Asia/Amman",
    "Asia/Anadyr",
    "Asia/Aqtau",
    "Asia/Aqtobe",
    "Asia/Ashgabat",
    "Asia/Atyrau",
    "Asia/Baghdad",
    "Asia/Baku",
    "Asia/Bangkok",
    "Asia/Barnaul",
    "Asia/Beirut",
    "Asia/Bishkek",
    "Asia/Chita",
    "Asia/Choibalsan",
    "Asia/Colombo",
    "Asia/Damascus",
    "Asia/Dhaka",
    "Asia/Dili",
    "Asia/Dubai",
    "Asia/Dushanbe",
    "Asia/Famagusta",
    "Asia/Gaza",
    "Asia/Hebron",
    "Asia/Ho_Chi_Minh",
    "Asia/Hong_Kong",
    "Asia/Hovd",
    "Asia/Irkutsk",
    "Asia/Jakarta",
    "Asia/Jayapura",
    "Asia/Jerusalem",
    "Asia/Kabul",
    "Asia/Kamchatka",
    "Asia/Karachi",
    "Asia/Kathmandu",
    "Asia/Khandyga",
    "Asia/Kolkata",
    "Asia/Krasnoyarsk",
    "Asia/Kuching",
    "Asia/Macau",
    "Asia/Magadan",
    "Asia/Makassar",
    "Asia/Manila",
    "Asia/Nicosia",
    "Asia/Novokuznetsk",
    "Asia/Novosibirsk",
    "Asia/Omsk",
    "Asia/Oral",
    "Asia/Pontianak",
    "Asia/Pyongyang",
    "Asia/Qatar",
    "Asia/Qostanay",
    "Asia/Qyzylorda",
    "Asia/Riyadh",
    "Asia/Sakhalin",
    "Asia/Samarkand",
    "Asia/Seoul",
    "Asia/Shanghai",
    "Asia/Singapore",
    "Asia/Srednekolymsk",
    "Asia/Taipei",
    "Asia/Tashkent",
    "Asia/Tbilisi",
    "Asia/Tehran",
    "Asia/Thimphu",
    "Asia/Tokyo",
    "Asia/Tomsk",
    "Asia/Ulaanbaatar",
    "Asia/Urumqi",
    "Asia/Ust-Nera",
    "Asia/Vladivostok",
    "Asia/Yakutsk",
    "Asia/Yangon",
    "Asia/Yekaterinburg",
    "Asia/Yerevan",
    "Atlantic/Azores",
    "Atlantic/Bermuda",
    "Atlantic/Canary",
    "Atlantic/Cape_Verde",
    "Atlantic/Faroe",
    "Atlantic/Madeira",
    "Atlantic/South_Georgia",
    "Atlantic/Stanley",
    "Australia/Adelaide",
    "Australia/Brisbane",
    "Australia/Broken_Hill",
    "Australia/Darwin",
    "Australia/Eucla",
    "Australia/Hobart",
    "Australia/Lindeman",
    "Australia/Lord_Howe",
    "Australia/Melbourne",
    "Australia/Perth",
    "Australia/Sydney",
    "Europe/Andorra",
    "Europe/Astrakhan",
    "Europe/Athens",
    "Europe/Belgrade",
    "Europe/Berlin",
    "Europe/Brussels",
    "Europe/Bucharest",
    "Europe/Budapest",
    "Europe/Chisinau",
    "Europe/Dublin",
    "Europe/Gibraltar",
    "Europe/Helsinki",
    "Europe/Istanbul",
    "Europe/Kaliningrad",
    "Europe/Kirov",
    "Europe/Kyiv",
    "Europe/Lisbon",
    "Europe/London",
    "Europe/Madrid",
    "Europe/Malta",
    "Europe/Minsk",
    "Europe/Moscow",
    "Europe/Paris",
    "Europe/Prague",
    "Europe/Riga",
    "Europe/Rome",
    "Europe/Samara",
    "Europe/Saratov",
    "Europe/Simferopol",
    "Europe/Sofia",
    "Europe/Tallinn",
    "Europe/Tirane",
    "Europe/Ulyanovsk",
    "Europe/Vienna",
    "Europe/Vilnius",
    "Europe/Volgograd",
    "Europe/Warsaw",
    "Europe/Zurich",
    "Indian/Chagos",
    "Indian/Maldives",
    "Indian/Mauritius",
    "Pacific/Apia",
    "Pacific/Auckland",
    "Pacific/Bougainville",
    "Pacific/Chatham",
    "Pacific/Easter",
    "Pacific/Efate",
    "Pacific/Fakaofo",
    "Pacific/Fiji",
    "Pacific/Galapagos",
    "Pacific/Gambier",
    "Pacific/Guadalcanal",
    "Pacific/Guam",
    "Pacific/Honolulu",
    "Pacific/Kanton",
    "Pacific/Kiritimati",
    "Pacific/Kosrae",
    "Pacific/Kwajalein",
    "Pacific/Marquesas",
    "Pacific/Nauru",
    "Pacific/Niue",
    "Pacific/Norfolk",
    "Pacific/Noumea",
    "Pacific/Pago_Pago",
    "Pacific/Palau",
    "Pacific/Pitcairn",
    "Pacific/Port_Moresby",
    "Pacific/Rarotonga",
    "Pacific/Tahiti",
    "Pacific/Tarawa",
    "Pacific/Tongatapu"
]