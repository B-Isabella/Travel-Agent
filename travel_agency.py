import flet as ft
import requests
import datetime


def get_country_info(name):
    try:
        country_url = f"https://restcountries.com/v3.1/name/{name}?fullText=true"
        res = requests.get(country_url)
        if res.status_code != 200:
            return None
        data = res.json()[0]

        lat, lon = data.get("latlng", [0, 0])
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(weather_url)

        temp_display = "N/A"
        if w_res.status_code == 200:
            celsius = w_res.json().get("current_weather", {}).get("temperature")
            fahrenheit = (celsius * 9 / 5) + 32
            temp_display = f"{celsius}°C / {fahrenheit:.1f}°F"

        return {
            "official_name": data.get("name", {}).get("official", "N/A"),
            "capital": data.get("capital", ["N/A"])[0],
            "region": f"{data.get('region')} ({data.get('subregion')})",
            "population": f"{data.get('population', 0):,}",
            "currency": ", ".join([c["name"] for c in data.get("currencies", {}).values()]),
            "languages": ", ".join(data.get("languages", {}).values()),
            "flag": data.get("flags", {}).get("png", ""),
            "timezones": ", ".join(data.get("timezones", [])),
            "weather": temp_display,
            "code": data.get("cca2"),
        }
    except:
        return None


def fetch_country_suggestions(query):
    try:
        response = requests.get(f"https://restcountries.com/v3.1/name/{query}")
        if response.status_code == 200:
            return [c["name"]["common"] for c in response.json()[:5]]
        return []
    except:
        return []


def main(page: ft.Page):
    page.title = "Global Travel Agency"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"
    page.padding = 20

    def SectionCard(content):
        return ft.Container(
            content=content,
            padding=20,
            bgcolor="#25292e",
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=15, color="#121212")
        )

    # TAB 1: COUNTRY SEARCH

    search_input = ft.TextField(
        label="Enter Country Name", width=400,
        border_radius=10, border_color="#448AFF"
    )
    suggestions_col = ft.Column(spacing=0)
    results_area = ft.Column(visible=False, spacing=15)

    def select_suggestion(name):
        search_input.value = name
        suggestions_col.controls = []
        page.update()

    def on_search_change(e):
        query = search_input.value.strip()
        if len(query) < 2:
            suggestions_col.controls = []
        else:
            names = fetch_country_suggestions(query)
            suggestions_col.controls = [
                ft.ListTile(
                    title=ft.Text(n),
                    on_click=lambda _, n=n: select_suggestion(n)
                ) for n in names
            ]
        page.update()

    def handle_search(e):
        data = get_country_info(search_input.value.strip())
        if not data:
            page.snack_bar = ft.SnackBar(ft.Text("Country not found!"))
            page.snack_bar.open = True
            page.update()
            return

        map_url = f"https://www.google.com/maps/search/{data['official_name'].replace(' ', '+')}"
        results_area.controls = [
            ft.Row([
                ft.Image(src=data["flag"], width=120, border_radius=5),
                ft.Column([
                    ft.Text(data["official_name"], size=22, weight="bold", color="#E3F2FD"),
                    ft.Text(f"🌡️ {data['weather']}", size=18, color="#64B5F6", weight="bold"),
                    ft.Text(f"📍 Capital: {data['capital']}", color="#90CAF9"),
                ])
            ]),
            ft.Divider(color="#424242"),
            ft.Text(f"🌐 Region: {data['region']}"),
            ft.Text(f"👥 Population: {data['population']}"),
            ft.Text(f"💱 Currency: {data['currency']}"),
            ft.Text(f"🗣️ Languages: {data['languages']}"),
            ft.Text(f"🕐 Time Zones: {data['timezones']}"),
            ft.Text(f"🆔 Country Code: {data['code']}"),
            ft.ElevatedButton(
                "View on Google Maps",
                icon=ft.Icons.MAP,
                bgcolor="#1976D2",
                color="white",
                on_click=lambda _: page.launch_url(map_url)
            )
        ]
        results_area.visible = True
        page.update()

    search_input.on_change = on_search_change

    tab1_ui = ft.Column([
        ft.Text("🌍 Global Discovery", size=32, weight="bold", color="#BBDEFB"),
        SectionCard(ft.Column([search_input, suggestions_col])),
        ft.ElevatedButton(
            "Search Details",
            icon=ft.Icons.TRAVEL_EXPLORE,
            bgcolor="#1976D2",
            color="white",
            on_click=handle_search
        ),
        results_area
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)

    # TAB 2: TRAVEL PLANNER

    plan_list = ft.Column(spacing=10)
    selected_date = {"val": None}
    date_text = ft.Text("No start date selected", italic=True, color="grey")

    client_name = ft.TextField(label="Client Full Name", width=400)

    dest_country = ft.TextField(label="Destination Country", width=400)
    dest_suggestions = ft.Column(spacing=0)

    duration = ft.TextField(
        label="Duration (days)", width=200,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    notes = ft.TextField(label="Additional Notes", multiline=True, width=400)

    def select_dest_suggestion(name):
        dest_country.value = name
        dest_suggestions.controls = []
        page.update()

    def on_dest_change(e):
        query = dest_country.value.strip()
        if len(query) < 2:
            dest_suggestions.controls = []
        else:
            names = fetch_country_suggestions(query)
            dest_suggestions.controls = [
                ft.ListTile(
                    title=ft.Text(n),
                    on_click=lambda _, n=n: select_dest_suggestion(n)
                ) for n in names
            ]
        page.update()

    def validate_days(e):
        filtered = "".join(c for c in duration.value if c.isdigit())
        if filtered != duration.value:
            duration.value = filtered
            page.update()

    dest_country.on_change = on_dest_change
    duration.on_change = validate_days

    def on_date_change(e):
        selected_date["val"] = e.control.value
        date_text.value = f"✈️ Departure: {e.control.value.strftime('%B %d, %Y')}"
        date_text.color = "white"
        date_text.italic = False
        page.update()

    def open_date_picker(e):
        page.open(ft.DatePicker(
            first_date=datetime.datetime.now(),
            last_date=datetime.datetime(2030, 12, 31),
            on_change=on_date_change,
        ))

    def add_plan(e):
        if not client_name.value.strip() or not dest_country.value.strip() or not duration.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("Please fill in Client Name, Destination, and Duration."))
            page.snack_bar.open = True
            page.update()
            return

        days = int(duration.value)
        start = selected_date["val"]
        if start:
            end_date = start + datetime.timedelta(days=days)
            date_range = f"{start.strftime('%b %d')} → {end_date.strftime('%b %d, %Y')}"
        else:
            date_range = "Dates TBD"

        extra = notes.value.strip()
        subtitle_text = date_range
        if extra:
            subtitle_text += f"  |  📝 {extra}"

        entry = ft.Container(
            bgcolor="#1e2124", padding=10, border_radius=10,
            content=ft.ListTile(
                leading=ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color="#64B5F6"),
                title=ft.Text(
                    f"{dest_country.value.strip()} — {client_name.value.strip()}",
                    weight="bold"
                ),
                subtitle=ft.Text(subtitle_text)
            ))

        def make_delete(e_container):
            def delete(_):
                plan_list.controls.remove(e_container)
                page.update()
            return delete

        entry.content.trailing = ft.IconButton(
            ft.Icons.DELETE, icon_color="red",
            on_click=make_delete(entry))

        plan_list.controls.append(entry)

        dest_country.value = ""
        duration.value = ""
        notes.value = ""
        selected_date["val"] = None
        date_text.value = "No start date selected"
        date_text.color = "grey"
        date_text.italic = True
        dest_suggestions.controls = []
        page.update()

    tab2_ui = ft.Column([
        ft.Text("🗺️ Itinerary Builder", size=28, weight="bold", color="#B2DFDB"),
        SectionCard(ft.Column([
            client_name,
            dest_country,
            dest_suggestions,
            ft.Row([
                ft.ElevatedButton(
                    "Pick Start Date",
                    icon=ft.Icons.CALENDAR_TODAY,
                    on_click=open_date_picker
                ),
                date_text
            ]),
            notes,
            ft.Row([
                duration,
                ft.ElevatedButton(
                    "Add to Plan",
                    icon=ft.Icons.ADD,
                    bgcolor="#00796B",
                    color="white",
                    on_click=add_plan
                )
            ])
        ])), 
        plan_list], 
        
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)

    # TAB 3: PRICING

    tab3_ui = ft.Column([
       ft.Text(" Pricing & Packages", size=28, weight="bold", color="#CE93D8"),
       SectionCard(ft.Text("...", italic=True))
   ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # TABS

    page.add(ft.Tabs(
        expand=True,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Search",  icon=ft.Icons.SEARCH,         content=tab1_ui),
            ft.Tab(text="Planner", icon=ft.Icons.EDIT_CALENDAR,  content=tab2_ui),
            ft.Tab(text="Pricing", icon=ft.Icons.PAYMENTS,       content=tab3_ui),
        ]))

ft.app(target=main)