from fastapi_hive.ioc_framework.autoconfigure import (
    evaluate_definitions,
    gather_autoconfigure_classes,
    sort_autoconfigure,
)
from fastapi_hive.ioc_framework.beans import BeanCondition, BeanDefinition
from fastapi_hive.ioc_framework.decorators import autoconfigure, conditional, provides
from fastapi_hive.ioc_framework.ioc_config import IoCConfig


def _defn(key, source="autoconfigure", **cond):
    return BeanDefinition(
        key=key,
        owner_cls=None,
        method_name=None,
        deps=[],
        source=source,
        conditions=BeanCondition(**cond),
        autoconfigure_name=cond.pop("name", None) if False else cond.get("name"),
    )


def test_on_import_skips_missing_package():
    config = IoCConfig()
    accepted = evaluate_definitions([
        BeanDefinition(
            key="ghost",
            owner_cls=None,
            method_name=None,
            deps=[],
            source="autoconfigure",
            conditions=BeanCondition(on_import="definitely_not_a_real_pkg_xyz"),
            autoconfigure_name="ghost",
        )
    ], config)
    assert accepted == []


def test_on_missing_yields_to_user_bean():
    @autoconfigure(name="hive.db")
    class Starter:
        @provides("db")
        def engine(self):
            return "starter"

    user = BeanDefinition(key="db", owner_cls=None, method_name=None, deps=[], source="scan")
    starter = BeanDefinition(
        key="db",
        owner_cls=Starter,
        method_name="engine",
        deps=[],
        source="autoconfigure",
        conditions=BeanCondition(on_missing="db"),
        autoconfigure_name="hive.db",
    )
    accepted = evaluate_definitions([user, starter], IoCConfig())
    assert [item.source for item in accepted] == ["scan"]


def test_on_bean_requires_existing_definition():
    accepted = evaluate_definitions([
        BeanDefinition(
            key="session",
            owner_cls=None,
            method_name=None,
            deps=[],
            source="autoconfigure",
            conditions=BeanCondition(on_bean="db"),
            autoconfigure_name="hive.session",
        )
    ], IoCConfig())
    assert accepted == []

    accepted = evaluate_definitions([
        BeanDefinition(key="db", owner_cls=None, method_name=None, deps=[], source="scan"),
        BeanDefinition(
            key="session",
            owner_cls=None,
            method_name=None,
            deps=["db"],
            source="autoconfigure",
            conditions=BeanCondition(on_bean="db"),
            autoconfigure_name="hive.session",
        ),
    ], IoCConfig())
    assert {item.key for item in accepted} == {"db", "session"}


def test_exclude_removes_autoconfigure_class():
    @autoconfigure(name="hive.db")
    class DbAuto:
        pass

    config = IoCConfig(AUTOCONFIGURE_EXCLUDE=["hive.db"])
    assert gather_autoconfigure_classes([DbAuto], config) == []


def test_after_before_orders_autoconfigure():
    @autoconfigure(name="late", after=["early"])
    class Late:
        pass

    @autoconfigure(name="early")
    class Early:
        pass

    assert sort_autoconfigure([Late, Early]) == [Early, Late]


def test_enabled_when_reads_features():
    accepted = evaluate_definitions([
        BeanDefinition(
            key="db",
            owner_cls=None,
            method_name=None,
            deps=[],
            source="autoconfigure",
            conditions=BeanCondition(enabled_when="db"),
            autoconfigure_name="hive.db",
        )
    ], IoCConfig(FEATURES={"db": False}))
    assert accepted == []

    accepted = evaluate_definitions([
        BeanDefinition(
            key="db",
            owner_cls=None,
            method_name=None,
            deps=[],
            source="autoconfigure",
            conditions=BeanCondition(enabled_when="db"),
            autoconfigure_name="hive.db",
        )
    ], IoCConfig(FEATURES={"db": True}))
    assert [item.key for item in accepted] == ["db"]
