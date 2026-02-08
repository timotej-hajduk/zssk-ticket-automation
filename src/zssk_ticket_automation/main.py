from zssk_ticket_automation.scraper import (
    get_train_stations,
    try_buy_ticket,
)


def main(start_station: str, end_station: str):
    stations = get_train_stations(start_station, end_station, "22:55")
    print(stations)
    try_buy_ticket(stations[0], stations[1])


if __name__ == "__main__":
    # main("Bratislava hl. st.", "Košice")
    print()
