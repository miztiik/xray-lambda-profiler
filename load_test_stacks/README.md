# Load Testing using Locust 🦗

[Locust](https://locust.io) helps you answer questions like, How many concurrent users you application can support?. Being written in python and the ability to script the tests, makes it my choice for quick and easy testing.

## Locust Installation

We will use Amazon Linux as base OS. From this machine we will target our test system/urls

  The following set gets the base OS packages,

```bash
sudo yum -y install python-pip python3 git
sudo yum -y install python3-setuptools python3-devel gcc
# sudo yum -y install libevent libevent-devel
```

The following set of packages install locustio

```bash
pip3 install gevent --user
pip3 install locustio --user
```

## Running Locust

  Write your test cases and save them in a file, preferably named `locustfile.py`

```bash
ROOT_URL="https://aws.amazon.com/blogs"

locust -f /var/locust/locustfile.py --master-host=18.212.126.161

locust -f /var/locust/locustfile.py --host=${ROOT_URL} --no-web --reset-stats --clients 10 --hatch-rate 100 --run-time 30s --only-summary

locust -f /var/locust/locustfile.py --host=${ROOT_URL} --no-web --clients 500 --hatch-rate 10 --run-time 4m55s --reset-stats --only-summary
# --clients The number of concurrent Locust users.
# --hatch-rate The rate per second in which clients are spawned.
# --run-time The number of seconds to run locust. ( Ensure enough time to hatch all users )
```

## 👋 Buy me a coffee

[Buy me](https://paypal.me/valaxy) a coffee ☕, _or_ You can reach out to get more details through [here](https://youtube.com/c/valaxytechnologies/about).

### 📚 References

1. [HomePage](https://locust.io/)

### 🏷️ Metadata

**Level**: 200
