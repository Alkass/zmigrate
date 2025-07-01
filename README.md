# zmigrate

## Dependencies
* libpq-dev
```
	apt-get install libpq-dev
```

## Author
[Fadi Hanna Al-Kass](https://github.com/alkass)

## Logging

``zmigrate`` uses Python's ``logging`` module for output. By default, it logs
at the ``INFO`` level. Set the ``ZMIGRATE_LOG_LEVEL`` environment variable to
override this default when running the CLI.
