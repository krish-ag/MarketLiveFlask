from flask import Flask, jsonify, session
from flask_session import Session
import requests
import time

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def getStocks():
    data = requests.get(
        f"https://bcast.slnbullion.com/VOTSBroadcastStreaming/Services/xml/GetLiveRateByTemplateID/sln?_={int(time.time())}")
    lst = data.text.split("\n")
    json_data = {}
    for i in lst:
        i = i.strip()
        if len(i) < 5:
            continue
        if i[0:3] not in ["137", "138", "139", "141", "163"]:
            continue
        name = i.split("\t")[1]
        if "($)" in name:
            if name not in json_data:
                json_data[name] = {"INR": i.split("\t")[2], "high": i.split("\t")[4], "low": i.split("\t")[5]}
            else:
                json_data[name]["INR"] = i.split("\t")[2]
                json_data[name]["high"] = i.split("\t")[4]
                json_data[name]["low"] = i.split("\t")[5]

        elif "INR" in name:
            json_data["USDINR"] = {"INR": i.split("\t")[2], "high": i.split("\t")[4], "low": i.split("\t")[5]}

        else:
            if "India " in name:
                name = name.replace("India ", "").strip()
            if name not in json_data:
                json_data[name] = {"INR": i.split("\t")[2], "high": i.split("\t")[4], "low": i.split("\t")[5]}
            else:
                json_data[name]["INR"] = i.split("\t")[2]
                json_data[name]["high"] = i.split("\t")[4]
                json_data[name]["low"] = i.split("\t")[5]

    oldmetal = session.get("oldmetal", {})
    if oldmetal:
        for i in json_data:
            if i in oldmetal:
                if json_data[i]["INR"] > oldmetal[i]["INR"]:
                    json_data[i]["Color"] = "#00ff00"
                elif json_data[i]["INR"] < oldmetal[i]["INR"]:
                    json_data[i]["Color"] = "#ff0000"

    session["oldmetal"] = json_data

    return json_data


def getNBSE():
    data = {}
    nifty = requests.get(
        "https://groww.in/v1/api/stocks_data/v1/accord_points/exchange/NSE/segment/CASH/latest_indices_ohlc/NIFTY")
    if nifty.json():
        nifty = nifty.json()
        data["Nifty 50"] = {"INR": nifty["value"], "high": nifty["high"], "low": nifty["low"]}

    sensex = requests.get(
        "https://groww.in/v1/api/stocks_data/v1/accord_points/exchange/BSE/segment/CASH/latest_indices_ohlc/SENSEX")
    if sensex.json():
        sensex = sensex.json()
        data["SENSEX"] = {"INR": sensex["value"], "high": sensex["high"], "low": sensex["low"]}

    oldstock = session.get("oldstock", {})

    if oldstock:
        for i in data:
            if i in oldstock:
                if data[i]["INR"] > oldstock[i]["INR"]:
                    data[i]["Color"] = "#00ff00"
                elif data[i]["INR"] < oldstock[i]["INR"]:
                    data[i]["Color"] = "#ff0000"

    session["oldstock"] = data
    return data


@app.route('/stock')
def getStock():
    return jsonify({
        "Metal": getStocks(),
        "Stock": getNBSE(),
    })


@app.route('/')
def privacy():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VDAMarket Privacy Policy</title>
    <style>
        /* Add your custom CSS styles here */
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }

        h1, h2 {
            color: #333;
        }

        p {
            margin-bottom: 15px;
        }

        a {
            color: #007BFF;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        footer {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ccc;
            color: #777;
            font-size: 0.8em;
        }
    </style>
</head>
<body>

    <header>
        <h1>VDAMarket Privacy Policy</h1>
    </header>

    <section>
        <h2>1. Information We Collect</h2>
        <p>
            <strong>1.1 Personal Information:</strong><br>
            We do not collect any personally identifiable information, such as names, addresses, or contact details.
        </p>
        <p>
            <strong>1.2 Non-Personal Information:</strong><br>
            We may collect non-personal information, including but not limited to:
            <ul>
                <li><strong>Device Information:</strong> We may collect information about your mobile device, including device type, operating system, and unique device identifiers.</li>
                <li><strong>Usage Information:</strong> We may collect information about how you use our app, such as the features you interact with and the duration of your sessions.</li>
            </ul>
        </p>
    </section>

    <section>
        <h2>2. How We Use Your Information</h2>
        <p>
            We only use the collected information for the purpose of improving and enhancing the functionality of our app. We do not sell, rent, or share your information with third parties.
        </p>
    </section>

    <section>
        <h2>3. Data Security</h2>
        <p>
            We prioritize the security of your information and use industry-standard measures to protect it from unauthorized access, disclosure, alteration, and destruction.
        </p>
    </section>

    <section>
        <h2>4. Third-Party Services</h2>
        <p>
            Our app may utilize third-party services, such as analytics tools. These services may collect information in accordance with their own privacy policies. We recommend reviewing the privacy policies of any third-party services used by our app.
        </p>
    </section>

    <section>
        <h2>5. Children's Privacy</h2>
        <p>
            Our app is not directed towards children under the age of 13. We do not knowingly collect personal information from children. If you are a parent or guardian and believe that your child has provided us with personal information, please contact us, and we will take steps to remove that information.
        </p>
    </section>

    <section>
        <h2>6. Changes to This Privacy Policy</h2>
        <p>
            We reserve the right to update our Privacy Policy. Any changes will be reflected in the app, and we encourage you to review the Privacy Policy periodically.
        </p>
    </section>

    <section>
        <h2>7. Contact Us</h2>
        <p>
            If you have any questions or concerns about this Privacy Policy, please contact us at <a href="mailto:printf.krish@gmail.com">printf.krish@gmail.com</a>.
        </p>
    </section>

    <footer>
        <p>&copy; 2024 VDAMarket. All rights reserved.</p>
    </footer>

</body>
</html>

    """


if __name__ == '__main__':
    app.run()
