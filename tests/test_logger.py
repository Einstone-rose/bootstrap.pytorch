import os
import pytest
import random

from bootstrap.lib.logger import Logger


def test_logger_init(tmpdir):
    Logger._instance = None
    Logger(dir_logs=tmpdir)
    
    assert os.path.isfile(Logger()._instance.sqlite_file)

    # check default _bootstrap table is empty
    statement = "SELECT * FROM _bootstrap"
    rows = Logger()._execute(statement).fetchall()
    assert rows == []


def test_nested_dict(tmpdir):
    Logger._instance = None
    Logger(dir_logs=tmpdir)
    Logger().log_dict('batch', {'loss': {'value': 0.42}})
    Logger().log_dict('epoch', {
        'timer': {
            'value': 0.42
        },
        'cpu': {
            'usage': {
                'float_value': 0.8,
            }
        }
    })


def test_new_key(tmpdir):
    Logger._instance = None
    Logger(dir_logs=tmpdir)
    Logger().log_dict('batch', {'loss': .22, 'metric': 0.232})
    with pytest.raises(Exception):
        Logger().log_dict('batch', {
            'loss': .22,
            'metric': 0.232,
            'new-metric': 0.42
        })


def test_missing_key(tmpdir):
    Logger._instance = None
    Logger(dir_logs=tmpdir)
    Logger().log_dict('batch', {'loss': .22, 'metric': 0.232})
    with pytest.raises(Exception):
        Logger().log_dict('batch', {'loss': .22})


def test_invalid_value(tmpdir):
    Logger._instance = None
    Logger(dir_logs=tmpdir)
    with pytest.raises(TypeError):
        Logger().log_dict('batch', {'loss': .22, 'metric': '0.232'})


def test_read(tmpdir):
    dicts = []
    for _ in range(3):
        dicts.append({'loss': .22, 'metric': 0.232})

    Logger._instance = None
    Logger(dir_logs=tmpdir)

    for batch_dict in dicts:
        Logger().log_dict('batch', batch_dict)

    statement = "SELECT loss,metric FROM _batch"
    rows = Logger()._execute(statement).fetchall()
    for (row, batch_dict) in zip(rows, dicts):
        assert row[0] == batch_dict['loss']
        assert row[1] == batch_dict['metric']
