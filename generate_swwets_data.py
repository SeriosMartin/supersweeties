"""
generate_sweets_data.py
Generates a single raw OLTP-style orders CSV for a UK sweet shop.

Known system bugs (by design, for realistic dirty data):
  - Customer 7  (Grace Pennington): product, quantity, price and payment fields
                                    always fail to populate
  - Customer 43 (Rebecca Ogden):    product and customer fields populate but
                                    unit_price and line_total are always blank
"""
from azure.identity import DefaultAzureCredential
import csv
import random
import os
from datetime import datetime, timedelta

# --- Config ---
OUTPUT_DIR = r"C:\oltp_data"

# --- 100 UK Customers (id, name, email, phone, town, region) ---
CUSTOMERS = [
    (1,   "Alice Hargreaves",    "alice.h@gmail.com",          "+44-7911-100001", "Manchester",       "North West"),
    (2,   "Bob Sutcliffe",       "bob.s@hotmail.co.uk",        "+44-7911-100002", "Leeds",            "Yorkshire"),
    (3,   "Carol Whitfield",     "carol.w@btinternet.com",     "+44-7911-100003", "Birmingham",       "West Midlands"),
    (4,   "David Ashworth",      "d.ashworth@gmail.com",       "+44-7911-100004", "Liverpool",        "North West"),
    (5,   "Emma Cartwright",     "emma.c@icloud.com",          "+44-7911-100005", "Bristol",          "South West"),
    (6,   "Frank Holloway",      "frank.h@outlook.com",        "+44-7911-100006", "Sheffield",        "Yorkshire"),
    (7,   "Grace Pennington",    "grace.p@gmail.com",          "+44-7911-100007", "Edinburgh",        "Scotland"),
    (8,   "Harry Blackwell",     "harry.b@hotmail.co.uk",      "+44-7911-100008", "Glasgow",          "Scotland"),
    (9,   "Isla Morrison",       "isla.m@gmail.com",           "+44-7911-100009", "Cardiff",          "Wales"),
    (10,  "Jack Thornton",       "jack.t@btinternet.com",      "+44-7911-100010", "Newcastle",        "North East"),
    (11,  "Karen Faulkner",      "karen.f@yahoo.co.uk",        "+44-7911-100011", "Nottingham",       "East Midlands"),
    (12,  "Liam Prescott",       "liam.p@gmail.com",           "+44-7911-100012", "Leicester",        "East Midlands"),
    (13,  "Megan Rowland",       "megan.r@outlook.com",        "+44-7911-100013", "Southampton",      "South East"),
    (14,  "Nathan Graves",       "nathan.g@gmail.com",         "+44-7911-100014", "Portsmouth",       "South East"),
    (15,  "Olivia Bradshaw",     "olivia.b@icloud.com",        "+44-7911-100015", "Oxford",           "South East"),
    (16,  "Paul Edmonds",        "paul.e@btinternet.com",      "+44-7911-100016", "Cambridge",        "East of England"),
    (17,  "Rachel Stirling",     "rachel.s@gmail.com",         "+44-7911-100017", "Norwich",          "East of England"),
    (18,  "Sam Whitaker",        "sam.w@hotmail.co.uk",        "+44-7911-100018", "Coventry",         "West Midlands"),
    (19,  "Tanya Hopwood",       "tanya.h@gmail.com",          "+44-7911-100019", "Stoke-on-Trent",   "West Midlands"),
    (20,  "Ursula Finch",        "ursula.f@yahoo.co.uk",       "+44-7911-100020", "Derby",            "East Midlands"),
    (21,  "Victor Langley",      "victor.l@gmail.com",         "+44-7911-100021", "Exeter",           "South West"),
    (22,  "Wendy Chambers",      "wendy.c@btinternet.com",     "+44-7911-100022", "Plymouth",         "South West"),
    (23,  "Xander Poole",        "xander.p@outlook.com",       "+44-7911-100023", "Swansea",          "Wales"),
    (24,  "Yvonne Hallett",      "yvonne.h@gmail.com",         "+44-7911-100024", "Belfast",          "Northern Ireland"),
    (25,  "Zoe Blackburn",       "zoe.b@icloud.com",           "+44-7911-100025", "Sunderland",       "North East"),
    (26,  "Aaron Whittle",       "aaron.w@gmail.com",          "+44-7911-100026", "Bradford",         "Yorkshire"),
    (27,  "Beth Crowther",       "beth.c@hotmail.co.uk",       "+44-7911-100027", "Hull",             "Yorkshire"),
    (28,  "Callum Fraser",       "callum.f@gmail.com",         "+44-7911-100028", "Aberdeen",         "Scotland"),
    (29,  "Diana Platt",         "diana.p@btinternet.com",     "+44-7911-100029", "Inverness",        "Scotland"),
    (30,  "Ethan Worrall",       "ethan.w@gmail.com",          "+44-7911-100030", "Wolverhampton",    "West Midlands"),
    (31,  "Fiona Dunbar",        "fiona.d@yahoo.co.uk",        "+44-7911-100031", "Peterborough",     "East of England"),
    (32,  "George Paxton",       "george.p@outlook.com",       "+44-7911-100032", "Luton",            "East of England"),
    (33,  "Hannah Skelton",      "hannah.s@gmail.com",         "+44-7911-100033", "Reading",          "South East"),
    (34,  "Ian Burrows",         "ian.b@btinternet.com",       "+44-7911-100034", "Milton Keynes",    "South East"),
    (35,  "Julia Kenyon",        "julia.k@gmail.com",          "+44-7911-100035", "Northampton",      "East Midlands"),
    (36,  "Kevin Slater",        "kevin.s@hotmail.co.uk",      "+44-7911-100036", "Ipswich",          "East of England"),
    (37,  "Laura Hewitt",        "laura.h@icloud.com",         "+44-7911-100037", "Chelmsford",       "East of England"),
    (38,  "Mark Tindall",        "mark.t@gmail.com",           "+44-7911-100038", "Gloucester",       "South West"),
    (39,  "Natalie Soper",       "natalie.s@outlook.com",      "+44-7911-100039", "Swindon",          "South West"),
    (40,  "Owen Griffiths",      "owen.g@gmail.com",           "+44-7911-100040", "Newport",          "Wales"),
    (41,  "Patricia Lowe",       "patricia.l@btinternet.com",  "+44-7911-100041", "Wrexham",          "Wales"),
    (42,  "Quentin Moss",        "quentin.m@gmail.com",        "+44-7911-100042", "Derry",            "Northern Ireland"),
    (43,  "Rebecca Ogden",       "rebecca.o@yahoo.co.uk",      "+44-7911-100043", "Dundee",           "Scotland"),
    (44,  "Stuart Neville",      "stuart.n@gmail.com",         "+44-7911-100044", "Perth",            "Scotland"),
    (45,  "Teresa Wheatley",     "teresa.w@hotmail.co.uk",     "+44-7911-100045", "Stirling",         "Scotland"),
    (46,  "Ulrich Barnes",       "ulrich.b@outlook.com",       "+44-7911-100046", "York",             "Yorkshire"),
    (47,  "Vanessa Holt",        "vanessa.h@gmail.com",        "+44-7911-100047", "Wakefield",        "Yorkshire"),
    (48,  "William Farrow",      "william.f@btinternet.com",   "+44-7911-100048", "Huddersfield",     "Yorkshire"),
    (49,  "Xena Clifford",       "xena.c@icloud.com",          "+44-7911-100049", "Barnsley",         "Yorkshire"),
    (50,  "Yasmin Patel",        "yasmin.p@gmail.com",         "+44-7911-100050", "Rotherham",        "Yorkshire"),
    (51,  "Zachary Hook",        "zachary.h@gmail.com",        "+44-7911-100051", "Salford",          "North West"),
    (52,  "Amber Dickinson",     "amber.d@hotmail.co.uk",      "+44-7911-100052", "Bolton",           "North West"),
    (53,  "Blake Armitage",      "blake.a@outlook.com",        "+44-7911-100053", "Wigan",            "North West"),
    (54,  "Clara Nuttall",       "clara.n@gmail.com",          "+44-7911-100054", "Warrington",       "North West"),
    (55,  "Dean Hartley",        "dean.h@btinternet.com",      "+44-7911-100055", "Stockport",        "North West"),
    (56,  "Elaine Radford",      "elaine.r@yahoo.co.uk",       "+44-7911-100056", "Preston",          "North West"),
    (57,  "Felix Oldham",        "felix.o@gmail.com",          "+44-7911-100057", "Blackpool",        "North West"),
    (58,  "Gemma Sykes",         "gemma.s@icloud.com",         "+44-7911-100058", "Carlisle",         "North West"),
    (59,  "Harvey Booth",        "harvey.b@gmail.com",         "+44-7911-100059", "Middlesbrough",    "North East"),
    (60,  "Ingrid Colley",       "ingrid.c@outlook.com",       "+44-7911-100060", "Durham",           "North East"),
    (61,  "Joel Ramsey",         "joel.r@gmail.com",           "+44-7911-100061", "Gateshead",        "North East"),
    (62,  "Kate Aldridge",       "kate.a@btinternet.com",      "+44-7911-100062", "Hartlepool",       "North East"),
    (63,  "Louis Brennan",       "louis.b@gmail.com",          "+44-7911-100063", "Shrewsbury",       "West Midlands"),
    (64,  "Maria Cope",          "maria.c@hotmail.co.uk",      "+44-7911-100064", "Hereford",         "West Midlands"),
    (65,  "Neil Denton",         "neil.d@gmail.com",           "+44-7911-100065", "Worcester",        "West Midlands"),
    (66,  "Ophelia Jennings",    "ophelia.j@yahoo.co.uk",      "+44-7911-100066", "Walsall",          "West Midlands"),
    (67,  "Peter Maguire",       "peter.m@outlook.com",        "+44-7911-100067", "Solihull",         "West Midlands"),
    (68,  "Quinn Draper",        "quinn.d@gmail.com",          "+44-7911-100068", "Telford",          "West Midlands"),
    (69,  "Rose Fitton",         "rose.f@icloud.com",          "+44-7911-100069", "Lincoln",          "East Midlands"),
    (70,  "Simon Clegg",         "simon.c@btinternet.com",     "+44-7911-100070", "Mansfield",        "East Midlands"),
    (71,  "Tara Leigh",          "tara.l@gmail.com",           "+44-7911-100071", "Chesterfield",     "East Midlands"),
    (72,  "Uma Sherwood",        "uma.s@hotmail.co.uk",        "+44-7911-100072", "Burton upon Trent","East Midlands"),
    (73,  "Vince Callaghan",     "vince.c@gmail.com",          "+44-7911-100073", "Cheltenham",       "South West"),
    (74,  "Wanda Frost",         "wanda.f@outlook.com",        "+44-7911-100074", "Bath",             "South West"),
    (75,  "Xavier Nunn",         "xavier.n@gmail.com",         "+44-7911-100075", "Taunton",          "South West"),
    (76,  "Yolanda Pierce",      "yolanda.p@btinternet.com",   "+44-7911-100076", "Torquay",          "South West"),
    (77,  "Zara Whitehead",      "zara.w@gmail.com",           "+44-7911-100077", "Truro",            "South West"),
    (78,  "Alfie Goodwin",       "alfie.g@yahoo.co.uk",        "+44-7911-100078", "Brighton",         "South East"),
    (79,  "Bella Sturges",       "bella.s@icloud.com",         "+44-7911-100079", "Eastbourne",       "South East"),
    (80,  "Connor Ash",          "connor.a@gmail.com",         "+44-7911-100080", "Guildford",        "South East"),
    (81,  "Daisy Holden",        "daisy.h@hotmail.co.uk",      "+44-7911-100081", "Maidstone",        "South East"),
    (82,  "Elliot Vane",         "elliot.v@gmail.com",         "+44-7911-100082", "Canterbury",       "South East"),
    (83,  "Freya Doyle",         "freya.d@outlook.com",        "+44-7911-100083", "Folkestone",       "South East"),
    (84,  "Gavin Marsh",         "gavin.m@btinternet.com",     "+44-7911-100084", "Colchester",       "East of England"),
    (85,  "Holly Birch",         "holly.b@gmail.com",          "+44-7911-100085", "Southend-on-Sea",  "East of England"),
    (86,  "Ivan Cross",          "ivan.c@yahoo.co.uk",         "+44-7911-100086", "Stevenage",        "East of England"),
    (87,  "Jade Harding",        "jade.h@gmail.com",           "+44-7911-100087", "Bedford",          "East of England"),
    (88,  "Kirk Lawson",         "kirk.l@icloud.com",          "+44-7911-100088", "Basildon",         "East of England"),
    (89,  "Lily Sutton",         "lily.s@gmail.com",           "+44-7911-100089", "Watford",          "East of England"),
    (90,  "Mason Todd",          "mason.t@hotmail.co.uk",      "+44-7911-100090", "St Albans",        "East of England"),
    (91,  "Nina Croft",          "nina.c@gmail.com",           "+44-7911-100091", "Lisburn",          "Northern Ireland"),
    (92,  "Oscar Plunkett",      "oscar.p@btinternet.com",     "+44-7911-100092", "Newry",            "Northern Ireland"),
    (93,  "Poppy Greer",         "poppy.g@outlook.com",        "+44-7911-100093", "Armagh",           "Northern Ireland"),
    (94,  "Rhys Vaughan",        "rhys.v@gmail.com",           "+44-7911-100094", "Bangor",           "Wales"),
    (95,  "Sienna Bowen",        "sienna.b@yahoo.co.uk",       "+44-7911-100095", "Llandudno",        "Wales"),
    (96,  "Theo Kingsmill",      "theo.k@gmail.com",           "+44-7911-100096", "Aberystwyth",      "Wales"),
    (97,  "Uma Talbot",          "uma.t@icloud.com",           "+44-7911-100097", "Bridgend",         "Wales"),
    (98,  "Violet Gough",        "violet.g@gmail.com",         "+44-7911-100098", "Merthyr Tydfil",   "Wales"),
    (99,  "Wade Sinclair",       "wade.s@hotmail.co.uk",       "+44-7911-100099", "Livingston",       "Scotland"),
    (100, "Xanthe Cromwell",     "xanthe.c@gmail.com",         "+44-7911-100100", "Falkirk",          "Scotland"),
]

# (product_id, name, category, price)
PRODUCTS = [
    (201, "Dark Choc 70% Bar 100g",         "Chocolate",       2.49),
    (202, "Milk Choc Hazelnut Bar 100g",     "Chocolate",       2.29),
    (203, "White Choc Raspberry Bar 90g",    "Chocolate",       2.59),
    (204, "Salted Caramel Choc Bar 100g",    "Chocolate",       2.79),
    (205, "Mint Crisp Dark Choc Bar 100g",   "Chocolate",       2.39),
    (206, "Luxury Truffle Box 12pc",         "Chocolate",       9.99),
    (207, "Praline Assortment 24pc",         "Chocolate",      16.50),
    (208, "Hot Choc Stirrer 3-pack",         "Chocolate",       5.99),
    (301, "Cola Bottles 200g",               "Gummies",         1.89),
    (302, "Sour Worms 200g",                 "Gummies",         1.99),
    (303, "Peach Rings 200g",                "Gummies",         1.89),
    (304, "Gummy Bears 400g Bag",            "Gummies",         3.49),
    (305, "Watermelon Slices 200g",          "Gummies",         2.10),
    (306, "Sour Cola Cubes 150g",            "Gummies",         1.75),
    (307, "Giant Strawbs 250g",              "Gummies",         2.25),
    (401, "Sherbet Lemons 150g",             "Hard Candy",      1.50),
    (402, "Pear Drops 150g",                 "Hard Candy",      1.50),
    (403, "Rhubarb & Custard 150g",          "Hard Candy",      1.60),
    (404, "Humbugs 200g",                    "Hard Candy",      1.70),
    (405, "Butter Mints 150g",               "Hard Candy",      1.45),
    (501, "Spearmint Gum 10-stick",          "Gum & Mints",     0.99),
    (502, "Peppermint Tic Tacs 100",         "Gum & Mints",     1.29),
    (503, "Bubblegum Strips 15-stick",       "Gum & Mints",     1.10),
    (504, "Sugar-Free Mints Tin 40g",        "Gum & Mints",     1.99),
    (601, "Rainbow Lollipop",                "Novelty",         0.50),
    (602, "Jawbreaker XXL",                  "Novelty",         0.75),
    (603, "Fizzy Dummies 150g",              "Novelty",         1.80),
    (604, "Rock Stick Seaside 30cm",         "Novelty",         2.00),
    (605, "Candy Necklace",                  "Novelty",         0.60),
    (701, "Pick & Mix 250g Bag",             "Pick & Mix",      3.50),
    (702, "Pick & Mix 500g Bag",             "Pick & Mix",      6.50),
    (703, "Pick & Mix 1kg Bag",              "Pick & Mix",     11.99),
    (801, "Clotted Cream Fudge 200g",        "Fudge & Toffee",  4.25),
    (802, "Chocolate Fudge 200g",            "Fudge & Toffee",  4.25),
    (803, "Treacle Toffee 150g",             "Fudge & Toffee",  2.99),
    (804, "Butter Toffees 200g",             "Fudge & Toffee",  3.10),
]

PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "apple_pay", "gift_card"]
SHIPPING        = ["standard", "express", "click_and_collect", "next_day"]

NOTES_POOL = [
    "", "", "", "", "", "", "", "", "",
    "birthday gift - please include card",
    "leave with neighbour",
    "do not bend packaging",
    "allergy note: nut allergy in household",
    "subscription box",
    "corporate order",
    "NULL",
    "n/a",
    "customer requested extra bubble wrap",
]

# Fri/Sat/Sun weighted heavier (0=Mon … 6=Sun)
DAY_WEIGHTS = {0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10, 4: 0.20, 5: 0.20, 6: 0.20}

def order_count_for_today():
    dow    = datetime.now().weekday()
    weight = DAY_WEIGHTS[dow]
    low    = int(100 + 900 * (weight - 0.10) / 0.10)
    low    = max(100, min(low, 550))
    return random.randint(low, 1000)

def rand_time_today():
    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight + timedelta(seconds=random.randint(0, 86399))

def make_orders(n):
    header = [
        "order_id", "order_datetime",
        "customer_id", "customer_name", "customer_email", "customer_phone",
        "customer_town", "customer_region",
        "product_id", "product_name", "category",
        "quantity", "unit_price", "line_total",
        "payment_method", "shipping_method", "status",
        "notes",
    ]
    status_pool = ["completed"] * 9 + ["cancelled"]

    # Bugged customer IDs (by design — simulates persistent system faults)
    BLANK_ITEM_AND_PAYMENT_CUSTOMER = 7   # Grace Pennington: product/qty/price/payment all blank
    BLANK_PRICE_CUSTOMER            = 43  # Rebecca Ogden: product populates but prices blank

    rows = []
    for i in range(1, n + 1):
        cust = random.choice(CUSTOMERS)
        prod = random.choice(PRODUCTS)
        qty  = random.randint(1, 12)

        cid = cust[0]
        dt  = rand_time_today().strftime("%Y-%m-%d %H:%M:%S")
        st  = random.choice(status_pool)
        nt  = random.choice(NOTES_POOL)

        if cid == BLANK_ITEM_AND_PAYMENT_CUSTOMER:
            # System bug: everything after customer region fails to populate
            row = [i, dt, cust[0], cust[1], cust[2], cust[3], cust[4], cust[5],
                   "", "", "", "", "", "", "", "", st, nt]
        elif cid == BLANK_PRICE_CUSTOMER:
            # System bug: product and quantity populate but price fields are blank
            row = [i, dt, cust[0], cust[1], cust[2], cust[3], cust[4], cust[5],
                   prod[0], prod[1], prod[2], qty, "", "",
                   random.choice(PAYMENT_METHODS), random.choice(SHIPPING), st, nt]
        else:
            price = prod[3]
            row = [i, dt, cust[0], cust[1], cust[2], cust[3], cust[4], cust[5],
                   prod[0], prod[1], prod[2], qty, price, round(qty * price, 2),
                   random.choice(PAYMENT_METHODS), random.choice(SHIPPING), st, nt]

        rows.append(row)
    return header, rows

from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
import io

def write_to_adls(csv_content: str, filename: str):
    service = DataLakeServiceClient(
        account_url="https://supersweeties.dfs.core.windows.net",
        credential=DefaultAzureCredential()
    )
    today = datetime.now()
    fs = service.get_file_system_client("landing")   # <-- your container name
    path = f"year={today.year}/month={today.month:02}/day={today.day:02}/{filename}"
    file_client = fs.get_file_client(path)
    encoded = csv_content.encode("utf-8")
    file_client.upload_data(encoded, overwrite=True, length=len(encoded))

def main():
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    n   = order_count_for_today()
    dow = datetime.now().strftime("%A")
    print(f"[{ts}] Generating sweets shop OLTP data ({dow} — {n} orders)...")

    orders_h, orders_d = make_orders(n)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(orders_h)
    writer.writerows(orders_d)

    write_to_adls(buf.getvalue(), f"orders_{ts}.csv")
    print("Done.")

if __name__ == "__main__":
    main()
