/**
 * Refactored Order Processing Module
 * Demonstrates clean code principles: single responsibility, early returns, and clear separation of concerns
 */

// Configuration objects replace complex if-else chains
const MEMBERSHIP_DISCOUNTS = {
  gold: 0.15,
  silver: 0.10,
  bronze: 0.05,
  default: 0
};

const COUPON_DISCOUNTS = {
  'SAVE20': 0.20,
  'SAVE10': 0.10,
  'SAVE5': 0.05
};

const SHIPPING_RATES = {
  under50: { express: 15, standard: 8, economy: 5 },
  under100: { express: 10, standard: 0, economy: 0 },
  over100: { express: 0, standard: 0, economy: 0 }
};

// =======================
// Validation Functions
// =======================

function validateInputs(order, user, inventory, paymentGateway, shippingService) {
  if (!order || !user || !inventory || !paymentGateway || !shippingService) {
    return { valid: false, error: 'Missing required parameters' };
  }
  return { valid: true };
}

function validateUser(user) {
  if (user.status !== 'active') {
    return { valid: false, error: 'User account is not active' };
  }
  if (!user.verified) {
    return { valid: false, error: 'User is not verified' };
  }
  return { valid: true };
}

function validateOrder(order) {
  if (!order.items || order.items.length === 0) {
    return { valid: false, error: 'Order has no items' };
  }
  return { valid: true };
}

// =======================
// Inventory Functions
// =======================

function checkItemAvailability(item, inventory) {
  const inventoryItem = inventory[item.id];

  if (!inventoryItem) {
    return { available: false, reason: 'Item not found' };
  }

  if (!inventoryItem.active) {
    return { available: false, reason: 'Item is inactive' };
  }

  if (inventoryItem.stock < item.quantity) {
    return { available: false, reason: 'Insufficient stock' };
  }

  return {
    available: true,
    itemDetails: {
      id: item.id,
      name: inventoryItem.name,
      quantity: item.quantity,
      price: inventoryItem.price,
      subtotal: inventoryItem.price * item.quantity
    }
  };
}

function processInventoryCheck(orderItems, inventory) {
  const availableItems = [];
  const unavailableItems = [];
  let totalPrice = 0;

  for (const item of orderItems) {
    const result = checkItemAvailability(item, inventory);

    if (result.available) {
      availableItems.push(result.itemDetails);
      totalPrice += result.itemDetails.subtotal;
    } else {
      unavailableItems.push({ id: item.id, reason: result.reason });
    }
  }

  return { availableItems, unavailableItems, totalPrice };
}

// =======================
// Pricing Functions
// =======================

function calculateMembershipDiscount(totalPrice, membershipLevel) {
  const discountRate = MEMBERSHIP_DISCOUNTS[membershipLevel] || MEMBERSHIP_DISCOUNTS.default;
  return totalPrice * discountRate;
}

function calculateCouponDiscount(totalPrice, couponCode) {
  if (!couponCode) return 0;
  const discountRate = COUPON_DISCOUNTS[couponCode] || 0;
  return totalPrice * discountRate;
}

function calculateTotalDiscount(totalPrice, user, couponCode) {
  const membershipDiscount = calculateMembershipDiscount(totalPrice, user.membershipLevel);
  const couponDiscount = calculateCouponDiscount(totalPrice, couponCode);
  return membershipDiscount + couponDiscount;
}

function getShippingTier(price) {
  if (price < 50) return 'under50';
  if (price < 100) return 'under100';
  return 'over100';
}

function calculateShippingCost(finalPrice, shippingMethod = 'standard') {
  const tier = getShippingTier(finalPrice);
  return SHIPPING_RATES[tier][shippingMethod] || 0;
}

function calculatePricing(totalPrice, user, order) {
  const discount = calculateTotalDiscount(totalPrice, user, order.couponCode);
  const finalPrice = totalPrice - discount;
  const shippingCost = calculateShippingCost(finalPrice, order.shippingMethod);
  const grandTotal = finalPrice + shippingCost;

  return { totalPrice, discount, finalPrice, shippingCost, grandTotal };
}

// =======================
// Payment Functions
// =======================

async function processPayment(paymentGateway, user, order, grandTotal) {
  try {
    const paymentResult = await paymentGateway.charge({
      userId: user.id,
      amount: grandTotal,
      currency: 'USD',
      description: `Order ${order.id}`
    });

    if (!paymentResult.success) {
      return { success: false, error: `Payment failed: ${paymentResult.error}` };
    }

    return { success: true, transactionId: paymentResult.transactionId };
  } catch (error) {
    return { success: false, error: `Payment error: ${error.message}` };
  }
}

// =======================
// Shipping Functions
// =======================

async function createShipment(shippingService, order, user, items) {
  try {
    const shipmentResult = await shippingService.createShipment({
      orderId: order.id,
      userId: user.id,
      address: user.shippingAddress,
      items: items,
      method: order.shippingMethod || 'standard'
    });

    if (!shipmentResult.success) {
      return { success: false, error: `Shipping failed: ${shipmentResult.error}` };
    }

    return {
      success: true,
      shipmentId: shipmentResult.shipmentId,
      estimatedDelivery: shipmentResult.estimatedDelivery
    };
  } catch (error) {
    return { success: false, error: `Shipping error: ${error.message}` };
  }
}

// =======================
// Inventory Management
// =======================

function updateInventoryStock(inventory, items) {
  for (const item of items) {
    inventory[item.id].stock -= item.quantity;
  }
}

function rollbackPayment(paymentGateway, transactionId) {
  try {
    paymentGateway.refund(transactionId);
  } catch (error) {
    console.error('Failed to rollback payment:', error);
  }
}

// =======================
// Main Orchestration Function
// =======================

async function processOrderRefactored(order, user, inventory, paymentGateway, shippingService) {
  // Validation with early returns
  const inputValidation = validateInputs(order, user, inventory, paymentGateway, shippingService);
  if (!inputValidation.valid) {
    return { success: false, error: inputValidation.error };
  }

  const userValidation = validateUser(user);
  if (!userValidation.valid) {
    return { success: false, error: userValidation.error };
  }

  const orderValidation = validateOrder(order);
  if (!orderValidation.valid) {
    return { success: false, error: orderValidation.error };
  }

  // Check inventory availability
  const { availableItems, unavailableItems, totalPrice } = processInventoryCheck(order.items, inventory);

  if (unavailableItems.length > 0) {
    return {
      success: false,
      error: 'Some items are unavailable',
      unavailableItems
    };
  }

  // Calculate pricing
  const pricing = calculatePricing(totalPrice, user, order);

  // Process payment
  const paymentResult = await processPayment(paymentGateway, user, order, pricing.grandTotal);
  if (!paymentResult.success) {
    return { success: false, error: paymentResult.error };
  }

  // Update inventory
  updateInventoryStock(inventory, availableItems);

  // Create shipment
  const shipmentResult = await createShipment(shippingService, order, user, availableItems);
  if (!shipmentResult.success) {
    rollbackPayment(paymentGateway, paymentResult.transactionId);
    return { success: false, error: shipmentResult.error };
  }

  // Return success response
  return {
    success: true,
    orderId: order.id,
    totalPrice: pricing.totalPrice,
    discount: pricing.discount,
    shippingCost: pricing.shippingCost,
    grandTotal: pricing.grandTotal,
    items: availableItems,
    paymentId: paymentResult.transactionId,
    shipmentId: shipmentResult.shipmentId,
    estimatedDelivery: shipmentResult.estimatedDelivery
  };
}

module.exports = {
  processOrderRefactored,
  // Export for testing
  validateInputs,
  validateUser,
  validateOrder,
  checkItemAvailability,
  processInventoryCheck,
  calculateMembershipDiscount,
  calculateCouponDiscount,
  calculateTotalDiscount,
  calculateShippingCost,
  calculatePricing,
  processPayment,
  createShipment,
  updateInventoryStock
};
