# Financal dashboard

# Requirements

- influxdb container running (influxdb2 used here)
- docker running

# Setup for normal linux machine

1. clone repo
2. create json config file `conf.json`
```json
{
    "categorys" : [
        "category 1",
        "category 2",
        "...",
    ],
    "user" : [
        "user 1"
    ],

    "targets" : [
        "user 1",
        "user 2"
    ],
    "db_conf" : {
        "org" : "<your-org>", 
        "bucket" : "<your bucket>",
        "token" : "<your-token>"
    }
}
```
3. run `build.sh build` to build image
4. run `build.sh run` to run container