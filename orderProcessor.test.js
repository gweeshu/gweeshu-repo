/**
 * Tests to verify that refactored version maintains the same behavior as the original
 */

const { processOrder } = require('./orderProcessor');
const { processOrderRefactored } = require('./orderProcessorRefactored');

// =======================
// Test Helpers
// =======================

function createMockPaymentGateway() {
  return {
    charge: ({ userId, amount, currency, description }) => ({
      success: true,
      transactionId: 'txn_' + Math.random().toString(36).substr(2, 9)
    }),
    refund: (transactionId) => ({ success: true })
  };
}

function createMockShippingService() {
  return {
    createShipment: ({ orderId, userId, address, items, method }) => ({
      success: true,
      shipmentId: 'ship_' + Math.random().toString(36).substr(2, 9),
      estimatedDelivery: '2026-01-23'
    })
  };
}

function createMockInventory() {
  return {
    'item1': { name: 'Widget A', price: 25, stock: 100, active: true },
    'item2': { name: 'Widget B', price: 50, stock: 50, active: true },
    'item3': { name: 'Widget C', price: 75, stock: 10, active: true },
    'item4': { name: 'Widget D', price: 100, stock: 5, active: false },
    'item5': { name: 'Widget E', price: 30, stock: 0, active: true }
  };
}

function createMockUser(overrides = {}) {
  return {
    id: 'user123',
    email: 'user@example.com',
    status: 'active',
    verified: true,
    membershipLevel: 'bronze',
    shippingAddress: {
      street: '123 Main St',
      city: 'Anytown',
      state: 'CA',
      zip: '12345'
    },
    ...overrides
  };
}

function createMockOrder(overrides = {}) {
  return {
    id: 'order123',
    items: [
      { id: 'item1', quantity: 2 },
      { id: 'item2', quantity: 1 }
    ],
    shippingMethod: 'standard',
    ...overrides
  };
}

// =======================
// Test Cases
// =======================

async function runTests() {
  console.log('Running Order Processor Tests...\n');
  let passed = 0;
  let failed = 0;

  // Test 1: Successful order processing
  console.log('Test 1: Successful order processing with standard shipping');
  try {
    const inventory = createMockInventory();
    const user = createMockUser();
    const order = createMockOrder();
    const payment = createMockPaymentGateway();
    const shipping = createMockShippingService();

    const original = await processOrder(order, user, inventory, payment, shipping);

    // Reset inventory for refactored test
    const inventory2 = createMockInventory();
    const refactored = await processOrderRefactored(order, user, inventory2, payment, shipping);

    if (original.success === refactored.success &&
        Math.abs(original.grandTotal - refactored.grandTotal) < 0.01) {
      console.log('✓ PASSED: Both versions produce same result');
      console.log(`  Grand Total: $${original.grandTotal.toFixed(2)}\n`);
      passed++;
    } else {
      console.log('✗ FAILED: Results differ');
      console.log('  Original:', original);
      console.log('  Refactored:', refactored);
      failed++;
    }
  } catch (error) {
    console.log('✗ FAILED:', error.message, '\n');
    failed++;
  }

  // Test 2: Inactive user
  console.log('Test 2: Order with inactive user');
  try {
    const inventory = createMockInventory();
    const user = createMockUser({ status: 'inactive' });
    const order = createMockOrder();
    const payment = createMockPaymentGateway();
    const shipping = createMockShippingService();

    const original = processOrder(order, user, inventory, payment, shipping);
    const refactored = await processOrderRefactored(order, user, createMockInventory(), payment, shipping);

    if (original.success === false && refactored.success === false) {
      console.log('✓ PASSED: Both versions reject inactive user');
      console.log(`  Error: ${refactored.error}\n`);
      passed++;
    } else {
      console.log('✗ FAILED: Results differ\n');
      failed++;
    }
  } catch (error) {
    console.log('✗ FAILED:', error.message, '\n');
    failed++;
  }

  // Test 3: Unverified user
  console.log('Test 3: Order with unverified user');
  try {
    const inventory = createMockInventory();
    const user = createMockUser({ verified: false });
    const order = createMockOrder();
    const payment = createMockPaymentGateway();
    const shipping = createMockShippingService();

    const original = processOrder(order, user, inventory, payment, shipping);
    const refactored = await processOrderRefactored(order, user, createMockInventory(), payment, shipping);

    if (original.success === false && refactored.success === false) {
      console.log('✓ PASSED: Both versions reject unverified user');
      console.log(`  Error: ${refactored.error}\n`);
      passed++;
    } else {
      console.log('✗ FAILED: Results differ\n');
      failed++;
    }
  } catch (error) {
    console.log('✗ FAILED:', error.message, '\n');
    failed++;
  }

  // Test 4: Out of stock item
  console.log('Test 4: Order with out of stock item');
  try {
    const inventory = createMockInventory();
    const user = createMockUser();
    const order = createMockOrder({
      items: [{ id: 'item5', quantity: 1 }] // item5 has 0 stock
    });
    const payment = createMockPaymentGateway();
    const shipping = createMockShippingService();

    const original = processOrder(order, user, inventory, payment, shipping);
    const refactored = await processOrderRefactored(order, user, createMockInventory(), payment, shipping);

    if (original.success === false && refactored.success === false) {
      console.log('✓ PASSED: Both versions detect out of stock');
      console.log(`  Error: ${refactored.error}\n`);
      passed++;
    } else {
      console.log('✗ FAILED: Results differ\n');
      failed++;
    }
  } catch (error) {
    console.log('✗ FAILED:', error.message, '\n');
    failed++;
  }

  // Test 5: Gold membership discount
  console.log('Test 5: Order with gold membership discount');
  try {
    const inventory = createMockInventory();
    const user = createMockUser({ membershipLevel: 'gold' });
    const order = createMockOrder({
      items: [{ id: 'item2', quantity: 2 }] // $100 total
    });
    const payment = createMockPaymentGateway();
    const shipping = createMockShippingService();

    const original = await processOrder(order, user, inventory, payment, shipping);
    const refactored = await processOrderRefactored(order, user, createMockInventory(), payment, shipping);

    if (original.success === refactored.success &&
        Math.abs(original.discount - refactored.discount) < 0.01) {
      console.log('✓ PASSED: Both versions calculate same discount');
      console.log(`  Discount: $${original.discount.toFixed(2)} (15%)\n`);
      passed++;
    } else {
      console.log('✗ FAILED: Discount calculation differs');
      console.log(`  Original discount: $${original.discount}`);
      console.log(`  Refactored discount: $${refactored.discount}\n`);
      failed++;
    }
  } catch (error) {
    console.log('✗ FAILED:', error.message, '\n');
    failed++;
  }

  // Test 6: Coupon code discount
  console.log('Test 6: Order with coupon code');
  try {
    const inventory = createMockInventory();
    const user = createMockUser({ membershipLevel: 'bronze' });
    const order = createMockOrder({
      items: [{ id: 'item2', quantity: 2 }],
      couponCode: 'SAVE20'
    });
    const payment = createMockPaymentGateway();
    const shipping = createMockShippingService();

    const original = await processOrder(order, user, inventory, payment, shipping);
    const refactored = await processOrderRefactored(order, user, createMockInventory(), payment, shipping);

    if (original.success === refactored.success &&
        Math.abs(original.discount - refactored.discount) < 0.01) {
      console.log('✓ PASSED: Both versions calculate same discount');
      console.log(`  Discount: $${original.discount.toFixed(2)} (5% membership + 20% coupon)\n`);
      passed++;
    } else {
      console.log('✗ FAILED: Discount calculation differs');
      console.log(`  Original discount: $${original.discount}`);
      console.log(`  Refactored discount: $${refactored.discount}\n`);
      failed++;
    }
  } catch (error) {
    console.log('✗ FAILED:', error.message, '\n');
    failed++;
  }

  // Test 7: Express shipping
  console.log('Test 7: Order with express shipping (under $50)');
  try {
    const inventory = createMockInventory();
    const user = createMockUser();
    const order = createMockOrder({
      items: [{ id: 'item1', quantity: 1 }], // $25 total
      shippingMethod: 'express'
    });
    const payment = createMockPaymentGateway();
    const shipping = createMockShippingService();

    const original = await processOrder(order, user, inventory, payment, shipping);
    const refactored = await processOrderRefactored(order, user, createMockInventory(), payment, shipping);

    if (original.success === refactored.success &&
        Math.abs(original.shippingCost - refactored.shippingCost) < 0.01) {
      console.log('✓ PASSED: Both versions calculate same shipping');
      console.log(`  Shipping Cost: $${original.shippingCost.toFixed(2)}\n`);
      passed++;
    } else {
      console.log('✗ FAILED: Shipping calculation differs');
      console.log(`  Original: $${original.shippingCost}`);
      console.log(`  Refactored: $${refactored.shippingCost}\n`);
      failed++;
    }
  } catch (error) {
    console.log('✗ FAILED:', error.message, '\n');
    failed++;
  }

  // Test 8: Free shipping on orders over $100
  console.log('Test 8: Free shipping on large order');
  try {
    const inventory = createMockInventory();
    const user = createMockUser();
    const order = createMockOrder({
      items: [
        { id: 'item2', quantity: 2 }, // $100
        { id: 'item1', quantity: 1 }  // $25
      ],
      shippingMethod: 'standard'
    });
    const payment = createMockPaymentGateway();
    const shipping = createMockShippingService();

    const original = await processOrder(order, user, inventory, payment, shipping);
    const refactored = await processOrderRefactored(order, user, createMockInventory(), payment, shipping);

    if (original.success === refactored.success &&
        original.shippingCost === 0 && refactored.shippingCost === 0) {
      console.log('✓ PASSED: Both versions apply free shipping\n');
      passed++;
    } else {
      console.log('✗ FAILED: Free shipping not applied correctly\n');
      failed++;
    }
  } catch (error) {
    console.log('✗ FAILED:', error.message, '\n');
    failed++;
  }

  // Summary
  console.log('='.repeat(50));
  console.log(`Test Results: ${passed} passed, ${failed} failed`);
  console.log('='.repeat(50));

  if (failed === 0) {
    console.log('\n✓ All tests passed! Refactored version maintains same behavior.');
  } else {
    console.log('\n✗ Some tests failed. Please review the differences.');
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  runTests();
}

module.exports = { runTests };
