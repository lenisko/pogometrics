import os
import time
import timeit
import yaml
import MySQLdb as msd
import logging
import datetime

config = yaml.safe_load(open("config.yml"))

logging.basicConfig(level=config["app"]["log_level"])
log = logging.getLogger(__name__)


def get_db_con(db_type: str) -> msd.connect:
    con = msd.connect(
        host=config[db_type]["host"],
        user=config[db_type]["user"],
        passwd=config[db_type]["password"],
        db=config[db_type]["name"],
        connect_timeout=config[db_type]["connect_timeout"],
    )

    return con


def save_sql_data(data: dict) -> None:
    execution_start = timeit.default_timer()

    con = get_db_con("metrics_db")
    cur = con.cursor()

    for table_name in data.keys():
        if not data[table_name]:  # skip empty
            continue

        # :cool:
        placeholders = ", ".join(["%s"] * len(data[table_name][0]))
        columns = ", ".join(data[table_name][0].keys())
        values = [tuple(v for v in row.values()) for row in data[table_name]]

        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, columns, placeholders)
        log.debug(f"SQL query: {sql}, VALUES: {values}")

        cur.executemany(sql, values)

    con.commit()
    con.close()

    execution_end = timeit.default_timer()
    log.debug(f"execution of save_sql_data took {execution_end - execution_start} sec")


def dt_now() -> str:
    value = datetime.datetime.utcnow()
    output = f"{value:%Y-%m-%d %H:%M:%S}"
    return output


def fetch_sql_data(bbox: list) -> dict:
    execution_start = timeit.default_timer()

    output = {
        "account": [],
        "counter": [],
        "raid": [],
    }

    # switches
    rdm_switch = config["rdm_db"]["enabled"]
    mad_switch = config["mad_db"]["enabled"]
    lorg_switch = config["lorg_db"]["enabled"]

    rdm_con, rdm_cur = None, None
    mad_con, mad_cur = None, None
    lorg_con, lorg_cur = None, None

    if rdm_switch:
        rdm_con = get_db_con("rdm_db")
        rdm_cur = rdm_con.cursor()

    if mad_switch:
        mad_con = get_db_con("mad_db")
        mad_cur = mad_con.cursor()

    if lorg_switch:
        lorg_con = get_db_con("lorg_db")
        lorg_cur = lorg_con.cursor()

    # RDM SECTION

    # account
    if rdm_switch and not config["skip"].get("rdm_account", True):
        rdm_cur.execute("""
            SELECT
                A.username,
                A.total_exp,
                A.level
            FROM
                account A INNER JOIN device D ON A.username = D.account_username
            WHERE
                A.total_exp is not NULL AND
                D.instance_name = 'level_instance'
            ORDER BY
                A.username ASC
        """)

        for row in rdm_cur.fetchall():
            output["account"].append({
                "ts": dt_now(),
                "source": 0,
                "username": row[0],
                "total_exp": row[1],
                "level": row[2],
            })

        log.debug("Fetched rdm account data")

    # pokemon_all
    if rdm_switch and not config["skip"].get("rdm_pokemon_all", True):
        rdm_cur.execute("""
            SELECT
                COUNT(*)
            FROM
                pokemon
            WHERE
                expire_timestamp > UNIX_TIMESTAMP() AND
                lon >= %s AND lon <= %s AND lat >= %s AND lat <= %s
        """, (bbox[0], bbox[2], bbox[1], bbox[3],)
        )

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": "pokemon_all",
                "counter": row[0],
            })

        log.debug("Fetched pokemon_all data")

    # pokemon_iv
    if rdm_switch and not config["skip"].get("rdm_pokemon_iv", True):
        rdm_cur.execute("""
            SELECT
                COUNT(*)
            FROM
                pokemon
            WHERE
                expire_timestamp > UNIX_TIMESTAMP() AND 
                iv IS NOT NULL AND
                lon >= %s AND lon <= %s AND lat >= %s AND lat <= %s
        """, (bbox[0], bbox[2], bbox[1], bbox[3],)
        )

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": "pokemon_iv",
                "counter": row[0],
            })

        log.debug("Fetched pokemon_iv data")

    # pokestop_quest
    if rdm_switch and not config["skip"].get("rdm_pokestop_quest", True):
        rdm_cur.execute("""
            SELECT
                COUNT(*)
            FROM
                pokestop
            WHERE
                quest_type is not null AND
                lon >= %s AND lon <= %s AND lat >= %s AND lat <= %s
        """, (bbox[0], bbox[2], bbox[1], bbox[3],)
        )

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": "pokestop_quest",
                "counter": row[0],
            })

        log.debug("Fetched pokestop_quest data")

    # pokestop_rocket
    if rdm_switch and not config["skip"].get("rdm_pokestop_rocket", True):
        rdm_cur.execute("""
            SELECT
                COUNT(*)
            FROM
                pokestop
            WHERE
                grunt_type is not null AND
                lon >= %s AND lon <= %s AND lat >= %s AND lat <= %s
        """, (bbox[0], bbox[2], bbox[1], bbox[3],)
        )

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": "pokestop_rocket",
                "counter": row[0],
            })

        log.debug("Fetched pokestop_rocket data")

    # raid
    if rdm_switch and not config["skip"].get("rdm_raid", True):
        rdm_cur.execute("""
            SELECT
                COUNT(*) total,
                SUM(CASE WHEN raid_level=1 THEN 1 ELSE 0 END) level1,
                SUM(CASE WHEN raid_level=2 THEN 1 ELSE 0 END) level2,
                SUM(CASE WHEN raid_level=3 THEN 1 ELSE 0 END) level3,
                SUM(CASE WHEN raid_level=4 THEN 1 ELSE 0 END) level4,
                SUM(CASE WHEN raid_level=5 THEN 1 ELSE 0 END) level5,
                SUM(CASE WHEN raid_level=6 THEN 1 ELSE 0 END) level6
            FROM
                gym
            WHERE
                raid_end_timestamp > UNIX_TIMESTAMP() AND
                lon >= %s AND lon <= %s AND lat >= %s AND lat <= %s
        """, (bbox[0], bbox[2], bbox[1], bbox[3],)
        )

        for row in rdm_cur.fetchall():
            output["raid"].append({
                "ts": dt_now(),
                "total": row[0],
                "level1": row[1] or 0,
                "level2": row[2] or 0,
                "level3": row[3] or 0,
                "level4": row[4] or 0,
                "level5": row[5] or 0,
                "level6": row[6] or 0,
            })

        log.debug("Fetched raid data")

    # banned_all
    if rdm_switch and not config["skip"].get("rdm_banned_all", True):
        rdm_cur.execute("SELECT count(*) FROM `account` WHERE banned")

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": "acc_banned_all",
                "counter": row[0],
            })

        log.debug("Fetched banned_all data")

    # banned_30
    if rdm_switch and not config["skip"].get("rdm_banned_30", True):
        rdm_cur.execute("SELECT count(*) FROM `account` WHERE level >= 30 and banned")

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": "acc_banned_30",
                "counter": row[0],
            })

        log.debug("Fetched banned_30 data")

    # acc_banned_{type}
    if rdm_switch and not config["skip"].get("rdm_banned_type", True):
        rdm_cur.execute("SELECT banned, count(*) FROM `account` group by banned")

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": f"acc_banned_{row[0]}".lower(),
                "counter": row[1],
            })

        log.debug("Fetched acc_banned_X data")

    # acc_in_use
    if rdm_switch and not config["skip"].get("rdm_acc_in_use", True):
        rdm_cur.execute("SELECT count(account_username) FROM `device` where account_username is not NULL")

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": "acc_in_use",
                "counter": row[0],
            })

        log.debug("Fetched acc_in_use data")

    # acc_clean_30
    if rdm_switch and not config["skip"].get("rdm_acc_clean_30", True):
        rdm_cur.execute("SELECT count(*) FROM `account` WHERE level >= 30 and not banned")

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": "acc_clean_30",
                "counter": row[0],
            })

        log.debug("Fetched acc_clean_30 data")

    # acc_failed_{type}
    if rdm_switch and not config["skip"].get("rdm_acc_failed_type", True):
        rdm_cur.execute("SELECT failed, count(*) FROM `account` group by failed")

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": f"acc_failed_{row[0]}".lower(),
                "counter": row[1],
            })

        log.debug("Fetched acc_failed_X data")

    # acc_warn_{type}
    if rdm_switch and not config["skip"].get("rdm_warn_type", True):
        rdm_cur.execute("SELECT warn, count(*) FROM `account` group by warn")

        for row in rdm_cur.fetchall():
            output["counter"].append({
                "ts": dt_now(),
                "name": f"acc_warn_{row[0]}".lower(),
                "counter": row[1],
            })

        log.debug("Fetched acc_warn_X data")

    # LORG SECTION
    if lorg_switch and not config["skip"].get("lorg_account", True):
        lorg_cur.execute(f"""
            SELECT
                username,
                total_exp,
                level
            FROM
                accounts
            WHERE
                device_id is not NULL
        """)

        for row in cur.fetchall():
            output["account"].append({
                "ts": dt_now(),
                "source": 1,
                "username": row[0],
                "total_exp": row[1],
                "level": row[2],
            })

        log.debug("Fetched lorg_account data")

    if rdm_switch:
        rdm_con.close()

    if mad_switch:
        mad_con.close()

    if lorg_switch:
        lorg_con.close()

    execution_end = timeit.default_timer()
    log.debug(f"execution of save_sql_data took {execution_end - execution_start} sec")

    return output


if __name__ == '__main__':
    log.info("Metrics script started")

    bbox = config["app"]["bbox"].split(",")
    bbox = list(map(float, bbox))

    log.warning(f"Limiting queries to bbox: {bbox}")
    log.warning(f'Sleep set to: {config["app"]["loop_sleep"]}')

    log.info("Starting loop")

    while True:
        try:
            log.info("Processing...")
            output = fetch_sql_data(bbox)
            log.info("Fetched data")
            save_sql_data(output)
            log.info("Saved data")

        except Exception as e:
            log.error(f"Catched loop error: {e}")

        finally:
            time.sleep(config["app"]["loop_sleep"])
