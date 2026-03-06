import flet as ft
import requests

def get_country_info(name):
    global country_link
    country_link = f"https://restcountries.com/v3.1/name/{name}?fullText=true"

    try:
        response = requests.get(country_link)
        if response.status_code != 200: 
            return None

        data = response.json()[0]
        lat, lon = data.get("latlng", [0, 0])

        weather_link = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_link)

        temp_display = "N/A"
        if weather_response.status_code == 200:
            celsius = weather_response.json().get('current_weather', {}).get('temperature')
            fahrenheit = (celsius * 9/5) + 32
            temp_display = f"{celsius}°C / {fahrenheit:.1f}°F"

        return {
            "official_name": data.get("name", {}).get("official", "N/A"),
            "capital": data.get("capital", ["N/A"])[0],
            "region": f"{data.get('region')} ({data.get('subregion')})",
            "population": f"{data.get('population', 0)}",
            "currency": ", ".join([c['name'] for c in data.get("currencies").values()]),
            "languages": ", ".join(data.get("languages").values()),
            "flag": data.get("flags", {}).get("png", ""),
            "timezones": ", ".join(data.get("timezones")),
            "weather": temp_display,
            "code": data.get("cca2")
        }
    except:
        return None

def main(page: ft.Page):
    page.title = "Global Travel Agency"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"

    #COUNTRY INFORMATION TAB -------------------------------------------------------------------------

    search_input = ft.TextField(label="Enter Country Name", width=400)
    suggestions1 = ft.Column(spacing=5)
    results_area = ft.Column(visible=False, spacing=15)
    results_area.visible = False
    page.update()

    def select_country(e):
        country_name = search_input.value.strip().lower()
        if len(country_name) < 2:
            suggestions1.controls = []
            page.update()
            return

        try:
            suggestions1.controls = []
            responsee = requests.get(f"https://restcountries.com/v3.1/name/{country_name}")
            dataa = responsee.json()

            for country in dataa[:5]:
                name = country["name"]["common"]
                suggestions1.controls.append(
                    ft.TextButton(text=name,
                    on_click=lambda e, n=name: choose_country(n))
                    )
            page.update()
        except:
            suggestions1.controls = []
            page.update()
            
    #this part will set destination to the option the user clicks from suggestions list.
    def choose_country(name):
        search_input.value = name
        suggestions1.controls = []
        page.update()

    def handle_search(e):

        country_data = get_country_info(search_input.value.strip())

        if country_data:
            results_area.controls = [
                    ft.Image(src=country_data["flag"], width=250, border_radius=10),
                    ft.Text(country_data["official_name"], size=28, weight="bold"),
                    ft.Text(f"📍 Capital: {country_data['capital']} | 🌡️ Weather: {country_data['weather']}", 
                            size=20, color="blue", weight="w600"),
                        ft.Divider(),
                        ft.Text(f"Region: {country_data['region']}"),
                        ft.Text(f"Population: {country_data['population']}"),
                        ft.Text(f"Currency: {country_data['currency']}"),
                        ft.Text(f"Languages: {country_data['languages']}"),
                        ft.Text(f"Time Zones: {country_data['timezones']}"),
                        ft.Text(f"Country Code: {country_data['code']}")
                    ]

            results_area.visible = True
        page.update()
    
    search_input.on_change = select_country

    #END OF COUNTRY INFORMATION TAB ---------------------------------------------------------------

    #Adding country information stuff to tab content
    tab1content = ft.Column([
        ft.Text("🌍 Travel Agency Search Portal", size=32, weight="bold"),
        search_input,
        suggestions1,
        ft.ElevatedButton("Search", icon=ft.Icons.SEARCH, on_click=handle_search),
        ft.Divider(),
        results_area
    ],
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    spacing=15
)   
    
    #TRAVEL PLAN TAB ----------------------------------------------------------------------------------

    #getting client information.
    client_name = ft.TextField(hint_text="Enter Full Name", width=400)
    destination_country = ft.TextField(hint_text="Enter Destination Country", width=400)
    suggestions = ft.Column(spacing=5)

    #function to get country suggestions as user types in destination text field
    def select_destination(e):
        #logic of this part: country_value is the stipped and lowercase value of what the user wrote in textfield. 
        #when the user writes up to 2 characters (len(country_value) will count this), suggestions turns into a list 
        #of the countries that match the country_value value
        country_value = destination_country.value.strip().lower()
        if len(country_value) < 2:
            suggestions.controls=[]
            page.update()
            return
        
        try:
            suggestions.controls = []
            responsee = requests.get(f"https://restcountries.com/v3.1/name/{country_value}")
            dataa = responsee.json()

            for country in dataa[:5]:
                name = country["name"]["common"]
                suggestions.controls.append(
                    ft.TextButton(text=name,
                    on_click=lambda e, n=name: choose_country(n))
                    )
            page.update()
        except:
            suggestions.controls = []
            page.update()
        
        #this part will set destination to the option the user clicks from suggestions list.
        def choose_country(name):
            destination_country.value = name
            suggestions.controls = []
            page.update()

    destination_country.on_change = select_destination


    #adding to 2nd tab content
    tab2content = ft.Column(
        [
            ft.Text("Create Travel Plan", size=28, weight="bold"),
            client_name,
            destination_country,
            suggestions
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    )

    #END OF TRAVEL PLAN TAB ---------------------------------------------------------------------------

    #Creating tabs
    tabs = ft.Tabs(selected_index=0,
                   animation_duration=300,
                     tabs=[
                          ft.Tab(text="Country Search", content=tab1content),
                          ft.Tab(text="Travel Plan", content=tab2content)
                     ])

    #Adding tabs
    page.add(tabs)

ft.app(target=main)