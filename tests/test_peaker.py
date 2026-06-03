import sys
import pytest

from peaker.peaker import main as peaker_main


def test_bad_mission(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['peaker',
                                      'art_credentials',
                                      '--mission', 'HST'])
    pytest.raises(ValueError, lambda: peaker_main())


def test_bad_period_format(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['peaker',
                                      'art_credentials',
                                      '--period', '2026/01/01-2026/02/02'])
    pytest.raises(ValueError, lambda: peaker_main())


def test_bad_xmldir(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['peaker',
                                      'art_credentials',
                                      '--xmldir', 'somewhere'])
    pytest.raises(FileNotFoundError, lambda: peaker_main())
