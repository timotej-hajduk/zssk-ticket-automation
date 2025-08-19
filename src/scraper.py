from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright.sync_api import sync_playwright

import asyncio


@dataclass
class TrainStationInfo:
    station: str
    time: str


def get_train_stations(start_station: str, end_station: str, depart_time: str) -> list[TrainStationInfo]:
    with sync_playwright() as p:
        with p.firefox.launch(headless=True) as browser:
            with browser.new_page() as page:
                page.goto("https://predaj.zssk.sk/search")
                page.get_by_placeholder("Nástupná stanica").fill(start_station)
                page.get_by_placeholder("Cieľová stanica").fill(end_station)
                page.locator("#departTime").fill(depart_time)
                page.click("#actionSearchConnectionButton")
                conn_list = page.locator("#connectionsList")
                conn_list.wait_for()
                assert conn_list.count() == 1

                day_connections = conn_list.locator(".dayConnections")
                first_day_connections = day_connections.first.locator(".row.connection-group")
                first_day_connections.first.click()
                expanded_connection = day_connections.locator(".row.connection-group.expanded")

                stations = expanded_connection.locator(".timeline-station").all()
                times = expanded_connection.locator(".timeline-time").all()
                station_infos = []
                for s, t in zip(stations, times):
                    station = s.text_content()
                    time = t.text_content()
                    if station and time:
                        station_infos.append(TrainStationInfo(station=station.strip(), time=time.strip()))
                return station_infos


def get_free_sections(train_station_infos: list[TrainStationInfo]):
    asyncio.run(get_free_sections_async(train_station_infos))


async def get_free_sections_async(train_station_infos: list[TrainStationInfo]):
    assert len(train_station_infos) > 1
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        tasks = [
            is_free_ticket_available(browser, start, end)
            for start, end in zip(train_station_infos, train_station_infos[1:])
        ]
        await asyncio.gather(*tasks)


async def is_free_ticket_available(
    browser: Browser, start_station: TrainStationInfo, end_station: TrainStationInfo
) -> bool:
    context: BrowserContext = await browser.new_context()
    page: Page = await context.new_page()
    await page.goto("https://predaj.zssk.sk/search")
    await page.get_by_placeholder("Nástupná stanica").fill(start_station.station)
    await page.get_by_placeholder("Cieľová stanica").fill(end_station.station)
    await page.locator("#departTime").fill(start_station.time)
    await page.click("#actionSearchConnectionButton")
    print()

    await context.close()
    return False


def try_buy_ticket(start_station: TrainStationInfo, end_station: TrainStationInfo):
    with sync_playwright() as p:
        with p.firefox.launch(headless=False) as browser:
            with browser.new_page() as page:
                page.goto("https://predaj.zssk.sk/search")
                page.get_by_placeholder("Nástupná stanica").fill(start_station.station)
                page.get_by_placeholder("Cieľová stanica").fill(end_station.station)
                page.locator("#departTime").fill(start_station.time)
                page.click("#actionSearchConnectionButton")

                conn_list = page.locator("#connectionsList")
                conn_list.wait_for()
                assert conn_list.count() == 1
                day_connections = conn_list.locator(".dayConnections")
                first_day_connections = day_connections.first.locator(".row.connection-group")
                first_day_connections.first.click()
                expanded_connection = day_connections.locator(".row.connection-group.expanded")
                buy_ticket_button = expanded_connection.locator("id=dayGroupLoop:0:eSalesConnectionLoop:0:j_idt379")
                buy_ticket_button.click()

                page.locator('[data-cy="ageCategory-0"] .btn-select-arrow.fa-angle-down').click()
                page.locator('[data-cy="ageCategoryList-0"] li', has_text="Mladý  16 - 25 r.").click()
                print()
