"""Integration test for FunPay Autopilot"""
import sys
import os
import asyncio
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_mock_integration():
    """Test Mock FunPay Integration"""
    from windows_app.integration.mock_integration import MockFunPayIntegration

    integration = MockFunPayIntegration()
    ok = await integration.authenticate({})
    assert ok, "Auth failed"

    products = await integration.get_products()
    assert len(products) == 5, f"Expected 5 products, got {len(products)}"
    print(f"[OK] Mock: {len(products)} products")

    market = await integration.get_product_market_data(products[0].id)
    assert len(market.competitors) > 0, "No competitors"
    print(f"[OK] Market: {len(market.competitors)} competitors for {products[0].name}")

    order = await integration.simulate_new_order()
    assert order.id, "Order has no ID"
    print(f"[OK] Order: #{order.id} - {order.product_name}")

    # Test price change
    result = await integration.update_product_price(products[0].id, 999)
    assert result, "Price change failed"
    print(f"[OK] Price changed to 999")

    # Test order processing
    orders = await integration.get_orders(status="paid")
    assert len(orders) > 0, "No paid orders"
    print(f"[OK] Orders: {len(orders)} paid orders")

    msg_ok = await integration.send_order_message(order.id, "Test message")
    assert msg_ok, "Message send failed"
    print(f"[OK] Message sent")

    complete_ok = await integration.complete_order(order.id)
    assert complete_ok, "Complete failed"
    print(f"[OK] Order completed")


def test_price_engine():
    """Test Price Recommendation Engine"""
    from backend.app.services.price_engine import PriceEngine, MarketData

    # Test balanced strategy
    mkt = MarketData(
        competitor_prices=[139, 145, 149, 152, 155, 160, 175, 180, 190],
        user_price=179,
        user_cost=100,
        user_min_price=120,
        user_max_price=200,
        user_desired_profit=30,
    )

    stats = PriceEngine.analyze_market(mkt)
    assert stats["min"] == 139
    assert stats["max"] == 190
    assert stats["count"] == 9
    print(f"[OK] Stats: min={stats['min']}, max={stats['max']}, avg={stats['avg']}, median={stats['median']}, pos=#{stats['position']}")

    # Test all strategies
    for strategy in ["max_profit", "max_sales", "balanced"]:
        rec = PriceEngine.recommend_price(mkt, strategy)
        assert rec.recommended_price >= mkt.user_min_price, f"{strategy}: below min!"
        assert rec.recommended_price <= mkt.user_max_price, f"{strategy}: above max!"
        assert rec.recommended_price >= mkt.user_cost + mkt.user_desired_profit, f"{strategy}: below profit floor!"
        print(f"[OK] {strategy}: {rec.recommended_price} RUB (position #{rec.position})")

    # max_sales should be lower than max_profit
    rec_sales = PriceEngine.recommend_price(mkt, "max_sales")
    rec_profit = PriceEngine.recommend_price(mkt, "max_profit")
    assert rec_sales.recommended_price <= rec_profit.recommended_price, "Sales should be <= Profit"
    print(f"[OK] Strategy ordering correct: sales({rec_sales.recommended_price}) <= profit({rec_profit.recommended_price})")


async def test_automation_engine():
    """Test Automation Engine with Mock"""
    from windows_app.integration.mock_integration import MockFunPayIntegration
    from windows_app.engine.automation_engine import AutomationEngine, AutomationRule, EngineStatus

    integration = MockFunPayIntegration()
    await integration.authenticate({})

    # Create engine (no backend running, so events won't be sent remotely)
    engine = AutomationEngine(
        integration=integration,
        backend_url="http://localhost:9999",  # Non-existent backend
        user_id="test_user",
        device_id="test_device",
    )

    # Collect events
    events = []
    engine.on_event(lambda e: events.append(e))

    # Add rule
    products = await integration.get_products()
    engine.add_rule(AutomationRule(
        product_id=products[0].id,
        enabled=True,
        auto_complete=True,
        auto_message=True,
        message_template="Test message for {product_name}",
        delivery_instructions="auto",
    ))

    # Simulate new order
    order = await integration.simulate_new_order()
    # Force order to be for our test product
    order.product_id = products[0].id
    order.product_name = products[0].name

    # Process order directly
    await engine._process_order(order)

    # Check events were emitted
    assert len(events) > 0, "No events emitted"
    event_types = [e.event_type for e in events]
    assert "NEW_ORDER" in event_types, "Missing NEW_ORDER event"
    assert "COMPLETE" in event_types, "Missing COMPLETE event"
    print(f"[OK] Engine: {len(events)} events emitted")
    for e in events:
        print(f"     {e.event_type}: {e.message}")

    await engine.cleanup()


def test_database_models():
    """Test database models are importable"""
    from backend.app.models.database import (
        Base, User, License, Product, Order, Payment,
        Notification, FeatureRequest, Device, AppVersion,
        Tariff, LicenseStatus, OrderStatus, EventType
    )
    print(f"[OK] All models importable, tables: {len(Base.metadata.tables)}")


async def test_backend_startup():
    """Test backend can start"""
    from backend.main import app
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test root
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "FunPay Autopilot"
        print(f"[OK] Backend root: {data['name']} v{data['version']}")

        # Test health
        resp = await client.get("/health")
        assert resp.status_code == 200
        print(f"[OK] Health: {resp.json()['status']}")

        # Test user registration
        resp = await client.post("/api/users/register", json={
            "telegram_id": 12345,
            "username": "testuser",
            "first_name": "Test",
        })
        assert resp.status_code == 200
        user_data = resp.json()
        assert "id" in user_data
        assert "referral_code" in user_data
        user_id = user_data["id"]
        print(f"[OK] User registered: {user_id}, ref={user_data['referral_code']}")

        # Test license check
        resp = await client.get(f"/api/licenses/check/{user_id}")
        assert resp.status_code == 200
        lic = resp.json()
        assert lic["valid"] == True
        assert lic["tariff"] == "TRIAL"
        assert lic["max_products"] == 3
        print(f"[OK] License: {lic['tariff']}, {lic['days_remaining']} days, max {lic['max_products']} products")

        # Test product creation
        resp = await client.post(f"/api/products/{user_id}", json={
            "name": "1000 Robux",
            "category": "Roblox",
            "price": 150,
            "cost": 100,
            "min_price": 120,
            "max_price": 200,
            "desired_profit": 30,
            "quantity": 10,
        })
        assert resp.status_code == 200
        product = resp.json()
        assert product["name"] == "1000 Robux"
        print(f"[OK] Product created: {product['id']}")

        # Test products list
        resp = await client.get(f"/api/products/{user_id}")
        assert resp.status_code == 200
        products = resp.json()
        assert len(products) >= 1
        print(f"[OK] Products list: {len(products)} items")

        # Test price recommendation
        resp = await client.post(
            f"/api/market/recommend/{product['id']}?strategy=balanced",
            json=[139, 145, 149, 152, 155, 160, 175]
        )
        assert resp.status_code == 200
        rec = resp.json()
        assert rec["recommended_price"] >= 120
        assert rec["recommended_price"] <= 200
        print(f"[OK] Price rec: {rec['recommended_price']} RUB, pos #{rec['position']}")

        # Test notifications
        resp = await client.get(f"/api/notifications/{user_id}")
        assert resp.status_code == 200
        print(f"[OK] Notifications endpoint works")

        # Test user stats
        resp = await client.get(f"/api/users/{user_id}/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["products"] >= 1
        print(f"[OK] Stats: {stats}")


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("  FUNPAY AUTOPILOT - TEST SUITE")
    print("=" * 60)

    print("\n--- Database Models ---")
    test_database_models()

    print("\n--- Price Engine ---")
    test_price_engine()

    print("\n--- Mock Integration ---")
    await test_mock_integration()

    print("\n--- Automation Engine ---")
    await test_automation_engine()

    print("\n--- Backend API ---")
    await test_backend_startup()

    print("\n" + "=" * 60)
    print("  ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
