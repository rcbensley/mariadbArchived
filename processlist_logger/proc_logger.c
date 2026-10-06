#include <mysql/plugin.h>
#include <mysql/plugin_audit.h>
#include <string.h>
#include <stdio.h>
#include <time.h>

static FILE *logfile = NULL;

/* Utility to get current timestamp as string */
static void get_timestamp(char *buffer, size_t size) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    strftime(buffer, size, "%Y-%m-%d %H:%M:%S", tm_info);
}

/* The audit callback */
static int my_audit_notify(MYSQL_THD thd,
                           mysql_event_class_t event_class,
                           const void *event)
{
    if (event_class != MYSQL_AUDIT_GENERAL_CLASS)
        return 0;

    const struct mysql_event_general *general_event = (const struct mysql_event_general *) event;
    if (!logfile)
        return 0;

    char timestamp[20];
    get_timestamp(timestamp, sizeof(timestamp));

    if (general_event->event_subclass == MYSQL_AUDIT_GENERAL_LOG_COMMAND_START) {
        fprintf(logfile, "START,%lu,%s,%s,%s,%s,\"%s\",%s,\n",
                general_event->thread_id,
                general_event->user ? general_event->user : "",
                general_event->host ? general_event->host : "",
                general_event->database ? general_event->database : "",
                general_event->command ? general_event->command : "",
                timestamp);
    } else if (general_event->event_subclass == MYSQL_AUDIT_GENERAL_LOG_COMMAND_END) {
        fprintf(logfile, "END,%lu,%s,%s,%s,%s,\"%s\",,%s\n",
                general_event->thread_id,
                general_event->user ? general_event->user : "",
                general_event->host ? general_event->host : "",
                general_event->database ? general_event->database : "",
                general_event->command ? general_event->command : "",
                timestamp);
    }

    fflush(logfile);
    return 0;
}

/* Initialization */
static int my_plugin_init(void *arg)
{
    logfile = fopen("/tmp/processlist_log.csv", "a");
    if (!logfile)
        return 1;
    return 0;
}

/* De-initialization */
static int my_plugin_deinit(void *arg)
{
    if (logfile) {
        fclose(logfile);
        logfile = NULL;
    }
    return 0;
}

static struct st_mysql_audit my_audit_descriptor =
{
    MYSQL_AUDIT_INTERFACE_VERSION,
    "processlist_logger",
    my_audit_notify,
    { MYSQL_AUDIT_GENERAL_CLASSMASK }
};

mysql_declare_plugin(my_simple_plugin)
{
    MYSQL_AUDIT_PLUGIN,
    &my_audit_descriptor,
    "processlist_logger",
    "Your Name",
    "Logs processlist entries to CSV",
    PLUGIN_LICENSE_GPL,
    my_plugin_init,
    my_plugin_deinit,
    0x0100,
    NULL,
    NULL,
    NULL,
    0,
}
mysql_declare_plugin_end;
