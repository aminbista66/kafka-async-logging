Redis Stack's geospatial feature allows you to query for data associated with geographic locations. You can either query for locations within a specific radius or based on geometric shapes, such as polygons. A polygon shape could, for instance, represent a lake or the layout of a building.

The examples in this article use the following schema:

| Field name       | Field type   |
| --------------   | ----------   |
| `store_location` | `GEO`        |
| `pickup_zone`    | `GEOSHAPE`   |


**Note**:
> Redis Stack version 7.2.0 or higher is required to use the `GEOSHAPE` field type.

```redis:[run_confirmation=true] Create the bike shop idx:bicycle
FT.CREATE
    idx:bicycle ON JSON
        PREFIX 1 bicycle:
    SCHEMA
        $.pickup_zone AS pickup_zone GEOSHAPE         // $.pickup_zone as GEOSHAPE
        $.store_location AS store_location GEO        // $.store_location as GEO
        $.brand AS brand TEXT WEIGHT 1.0
        $.model AS model TEXT WEIGHT 1.0
        $.description AS description TEXT WEIGHT 1.0
        $.price AS price NUMERIC
        $.condition AS condition TAG SEPARATOR ,
```

```redis:[run_confirmation=true] Load the JSON data
JSON.SET "bicycle:0" "." "{\"pickup_zone\": \"POLYGON((-74.0610 40.7578, -73.9510 40.7578, -73.9510 40.6678, -74.0610 40.6678, -74.0610 40.7578))\", \"store_location\": \"-74.0060,40.7128\", \"brand\": \"Velorim\", \"model\": \"Jigger\", \"price\": 270, \"description\": \"Small and powerful, the Jigger is the best ride for the smallest of tikes! This is the tiniest kids\\u2019 pedal bike on the market available without a coaster brake, the Jigger is the vehicle of choice for the rare tenacious little rider raring to go.\", \"condition\": \"new\"}"
JSON.SET "bicycle:1" "." "{\"pickup_zone\": \"POLYGON((-118.2887 34.0972, -118.1987 34.0972, -118.1987 33.9872, -118.2887 33.9872, -118.2887 34.0972))\", \"store_location\": \"-118.2437,34.0522\", \"brand\": \"Bicyk\", \"model\": \"Hillcraft\", \"price\": 1200, \"description\": \"Kids want to ride with as little weight as possible. Especially on an incline! They may be at the age when a 27.5\\\" wheel bike is just too clumsy coming off a 24\\\" bike. The Hillcraft 26 is just the solution they need!\", \"condition\": \"used\"}"
JSON.SET "bicycle:2" "." "{\"pickup_zone\": \"POLYGON((-87.6848 41.9331, -87.5748 41.9331, -87.5748 41.8231, -87.6848 41.8231, -87.6848 41.9331))\", \"store_location\": \"-87.6298,41.8781\", \"brand\": \"Nord\", \"model\": \"Chook air 5\", \"price\": 815, \"description\": \"The Chook Air 5  gives kids aged six years and older a durable and uberlight mountain bike for their first experience on tracks and easy cruising through forests and fields. The lower  top tube makes it easy to mount and dismount in any situation, giving your kids greater safety on the trails.\", \"condition\": \"used\"}"
JSON.SET "bicycle:3" "." "{\"pickup_zone\": \"POLYGON((-80.2433 25.8067, -80.1333 25.8067, -80.1333 25.6967, -80.2433 25.6967, -80.2433 25.8067))\", \"store_location\": \"-80.1918,25.7617\", \"brand\": \"Eva\", \"model\": \"Eva 291\", \"price\": 3400, \"description\": \"The sister company to Nord, Eva launched in 2005 as the first and only women-dedicated bicycle brand. Designed by women for women, allEva bikes are optimized for the feminine physique using analytics from a body metrics database. If you like 29ers, try the Eva 291. It\\u2019s a brand new bike for 2022.. This full-suspension, cross-country ride has been designed for velocity. The 291 has 100mm of front and rear travel, a superlight aluminum frame and fast-rolling 29-inch wheels. Yippee!\", \"condition\": \"used\"}"
JSON.SET "bicycle:4" "." "{\"pickup_zone\": \"POLYGON((-122.4644 37.8199, -122.3544 37.8199, -122.3544 37.7099, -122.4644 37.7099, -122.4644 37.8199))\", \"store_location\": \"-122.4194,37.7749\", \"brand\": \"Noka Bikes\", \"model\": \"Kahuna\", \"price\": 3200, \"description\": \"Whether you want to try your hand at XC racing or are looking for a lively trail bike that's just as inspiring on the climbs as it is over rougher ground, the Wilder is one heck of a bike built specifically for short women. Both the frames and components have been tweaked to include a women\\u2019s saddle, different bars and unique colourway.\", \"condition\": \"used\"}"
JSON.SET "bicycle:5" "." "{\"pickup_zone\": \"POLYGON((-0.1778 51.5524, 0.0822 51.5524, 0.0822 51.4024, -0.1778 51.4024, -0.1778 51.5524))\", \"store_location\": \"-0.1278,51.5074\", \"brand\": \"Breakout\", \"model\": \"XBN 2.1 Alloy\", \"price\": 810, \"description\": \"The XBN 2.1 Alloy is our entry-level road bike \\u2013 but that\\u2019s not to say that it\\u2019s a basic machine. With an internal weld aluminium frame, a full carbon fork, and the slick-shifting Claris gears from Shimano\\u2019s, this is a bike which doesn\\u2019t break the bank and delivers craved performance.\", \"condition\": \"new\"}"
JSON.SET "bicycle:6" "." "{\"pickup_zone\": \"POLYGON((2.1767 48.9016, 2.5267 48.9016, 2.5267 48.5516, 2.1767 48.5516, 2.1767 48.9016))\", \"store_location\": \"2.3522,48.8566\", \"brand\": \"ScramBikes\", \"model\": \"WattBike\", \"price\": 2300, \"description\": \"The WattBike is the best e-bike for people who still feel young at heart. It has a Bafang 1000W mid-drive system and a 48V 17.5AH Samsung Lithium-Ion battery, allowing you to ride for more than 60 miles on one charge. It\\u2019s great for tackling hilly terrain or if you just fancy a more leisurely ride. With three working modes, you can choose between E-bike, assisted bicycle, and normal bike modes.\", \"condition\": \"new\"}"
JSON.SET "bicycle:7" "." "{\"pickup_zone\": \"POLYGON((13.3260 52.5700, 13.6550 52.5700, 13.6550 52.2700, 13.3260 52.2700, 13.3260 52.5700))\", \"store_location\": \"13.4050,52.5200\", \"brand\": \"Peaknetic\", \"model\": \"Secto\", \"price\": 430, \"description\": \"If you struggle with stiff fingers or a kinked neck or back after a few minutes on the road, this lightweight, aluminum bike alleviates those issues and allows you to enjoy the ride. From the ergonomic grips to the lumbar-supporting seat position, the Roll Low-Entry offers incredible comfort. The rear-inclined seat tube facilitates stability by allowing you to put a foot on the ground to balance at a stop, and the low step-over frame makes it accessible for all ability and mobility levels. The saddle is very soft, with a wide back to support your hip joints and a cutout in the center to redistribute that pressure. Rim brakes deliver satisfactory braking control, and the wide tires provide a smooth, stable ride on paved roads and gravel. Rack and fender mounts facilitate setting up the Roll Low-Entry as your preferred commuter, and the BMX-like handlebar offers space for mounting a flashlight, bell, or phone holder.\", \"condition\": \"new\"}"
JSON.SET "bicycle:8" "." "{\"pickup_zone\": \"POLYGON((1.9450 41.4301, 2.4018 41.4301, 2.4018 41.1987, 1.9450 41.1987, 1.9450 41.4301))\", \"store_location\": \"2.1734, 41.3851\", \"brand\": \"nHill\", \"model\": \"Summit\", \"price\": 1200, \"description\": \"This budget mountain bike from nHill performs well both on bike paths and on the trail. The fork with 100mm of travel absorbs rough terrain. Fat Kenda Booster tires give you grip in corners and on wet trails. The Shimano Tourney drivetrain offered enough gears for finding a comfortable pace to ride uphill, and the Tektro hydraulic disc brakes break smoothly. Whether you want an affordable bike that you can take to work, but also take trail in mountains on the weekends or you\\u2019re just after a stable, comfortable ride for the bike path, the Summit gives a good value for money.\", \"condition\": \"new\"}"
JSON.SET "bicycle:9" "." "{\"pickup_zone\": \"POLYGON((12.4464 42.1028, 12.5464 42.1028, 12.5464 41.7028, 12.4464 41.7028, 12.4464 42.1028))\", \"store_location\": \"12.4964,41.9028\", \"model\": \"ThrillCycle\", \"brand\": \"BikeShind\", \"price\": 815, \"description\": \"An artsy,  retro-inspired bicycle that\\u2019s as functional as it is pretty: The ThrillCycle steel frame offers a smooth ride. A 9-speed drivetrain has enough gears for coasting in the city, but we wouldn\\u2019t suggest taking it to the mountains. Fenders protect you from mud, and a rear basket lets you transport groceries, flowers and books. The ThrillCycle comes with a limited lifetime warranty, so this little guy will last you long past graduation.\", \"condition\": \"refurbished\"}"
```

## Radius

You can construct a radius query by passing the center coordinates (longitude, latitude), the radius, and the distance unit to the `FT.SEARCH` command.

```
FT.SEARCH index "@geo_field:[lon lat radius unit]"
```

Allowed units are `m`, `km`, `mi`, and `ft`.

The following query finds all bicycle stores within a radius of 20 miles around London:

```redis Radius query
FT.SEARCH idx:bicycle "@store_location:[-0.1778 51.5524 20 mi]"
```

## Shape

The only supported shapes are points and polygons. You can query for polygons or points that either contain or are within a given geometric shape.

```
FT.SEARCH index "@geo_shape_field:[{WITHIN|CONTAINS} $shape] PARAMS 2 shape "shape_as_wkt" DIALECT 3
```

Here is a more detailed explanation of this query:

1. **Field name**: you need to replace `geo_shape_field` with the `GEOSHAPE` field's name on which you want to query.
2. **Spatial operator**: spatial operators define the relationship between the shapes in the database and the shape you are searching for. You can either use `WITHIN` or `CONTAINS`. `WITHIN` finds any shape in the database that is inside the given shape. `CONTAINS` queries for any shape that surrounds the given shape.
3. **Parameter**: the query refers to a parameter named `shape`. You can use any parameter name here. You need to use the `PARAMS` clause to set the parameter value. The value follows the [well-known text representation of a geometry](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry). Supported types are `POINT(x y)` and `POLYGON((x1 y1, x2 y2, ...))`.
4. **Dialect**: Shape-based queries have been available since version three of the query dialect.

The following example query verifies if a bicycle is within a pickup zone:

```redis Shape query 1
FT.SEARCH idx:bicycle "@pickup_zone:[CONTAINS $bike]" PARAMS 2 bike "POINT(-0.1278 51.5074)" DIALECT 3
```

If you want to find all pickup zones that are approximately within Europe, then you can use the following query:

```redis Shape query 2
FT.SEARCH idx:bicycle "@pickup_zone:[WITHIN $europe]" PARAMS 2 europe "POLYGON((-25 35, 40 35, 40 70, -25 70, -25 35))" DIALECT 3
```
