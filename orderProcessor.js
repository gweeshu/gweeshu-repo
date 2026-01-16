/**
 * Complex Order Processing Function
 * This function demonstrates common code smells and complexity issues
 */

// Original Complex Function - BEFORE REFACTORING
function processOrder(order, user, inventory, paymentGateway, shippingService) {
  // Validate inputs
  if (!order || !user || !inventory || !paymentGateway || !shippingService) {
    return { success: false, error: 'Missing required parameters' };
  }

  // Check user status and order details
  if (user.status === 'active') {
    if (user.verified === true) {
      if (order.items && order.items.length > 0) {
        let totalPrice = 0;
        let availableItems = [];
        let unavailableItems = [];

        // Check inventory for each item
        for (let i = 0; i < order.items.length; i++) {
          const item = order.items[i];
          if (inventory[item.id]) {
            if (inventory[item.id].stock >= item.quantity) {
              if (inventory[item.id].active === true) {
                totalPrice += inventory[item.id].price * item.quantity;
                availableItems.push({
                  id: item.id,
                  name: inventory[item.id].name,
                  quantity: item.quantity,
                  price: inventory[item.id].price,
                  subtotal: inventory[item.id].price * item.quantity
                });
              } else {
                unavailableItems.push({ id: item.id, reason: 'Item is inactive' });
              }
            } else {
              unavailableItems.push({ id: item.id, reason: 'Insufficient stock' });
            }
          } else {
            unavailableItems.push({ id: item.id, reason: 'Item not found' });
          }
        }

        // Process payment if all items are available
        if (unavailableItems.length === 0) {
          // Apply discounts
          let discount = 0;
          if (user.membershipLevel === 'gold') {
            discount = totalPrice * 0.15;
          } else if (user.membershipLevel === 'silver') {
            discount = totalPrice * 0.10;
          } else if (user.membershipLevel === 'bronze') {
            discount = totalPrice * 0.05;
          }

          if (order.couponCode) {
            if (order.couponCode === 'SAVE20') {
              discount += totalPrice * 0.20;
            } else if (order.couponCode === 'SAVE10') {
              discount += totalPrice * 0.10;
            } else if (order.couponCode === 'SAVE5') {
              discount += totalPrice * 0.05;
            }
          }

          const finalPrice = totalPrice - discount;

          // Calculate shipping
          let shippingCost = 0;
          if (finalPrice < 50) {
            if (order.shippingMethod === 'express') {
              shippingCost = 15;
            } else if (order.shippingMethod === 'standard') {
              shippingCost = 8;
            } else {
              shippingCost = 5;
            }
          } else if (finalPrice < 100) {
            if (order.shippingMethod === 'express') {
              shippingCost = 10;
            } else {
              shippingCost = 0; // Free standard shipping
            }
          } else {
            shippingCost = 0; // Free shipping for orders over $100
          }

          const grandTotal = finalPrice + shippingCost;

          // Process payment
          try {
            const paymentResult = paymentGateway.charge({
              userId: user.id,
              amount: grandTotal,
              currency: 'USD',
              description: `Order ${order.id}`
            });

            if (paymentResult.success) {
              // Update inventory
              for (let i = 0; i < availableItems.length; i++) {
                const item = availableItems[i];
                inventory[item.id].stock -= item.quantity;
              }

              // Create shipment
              try {
                const shipmentResult = shippingService.createShipment({
                  orderId: order.id,
                  userId: user.id,
                  address: user.shippingAddress,
                  items: availableItems,
                  method: order.shippingMethod || 'standard'
                });

                if (shipmentResult.success) {
                  // Send confirmation email
                  const emailData = {
                    to: user.email,
                    subject: 'Order Confirmation',
                    body: `Your order ${order.id} has been confirmed. Total: $${grandTotal.toFixed(2)}`
                  };

                  return {
                    success: true,
                    orderId: order.id,
                    totalPrice: totalPrice,
                    discount: discount,
                    shippingCost: shippingCost,
                    grandTotal: grandTotal,
                    items: availableItems,
                    paymentId: paymentResult.transactionId,
                    shipmentId: shipmentResult.shipmentId,
                    estimatedDelivery: shipmentResult.estimatedDelivery
                  };
                } else {
                  // Refund payment if shipping fails
                  paymentGateway.refund(paymentResult.transactionId);
                  return { success: false, error: 'Shipping failed: ' + shipmentResult.error };
                }
              } catch (shipmentError) {
                // Refund payment if shipping throws error
                paymentGateway.refund(paymentResult.transactionId);
                return { success: false, error: 'Shipping error: ' + shipmentError.message };
              }
            } else {
              return { success: false, error: 'Payment failed: ' + paymentResult.error };
            }
          } catch (paymentError) {
            return { success: false, error: 'Payment error: ' + paymentError.message };
          }
        } else {
          return { success: false, error: 'Some items are unavailable', unavailableItems: unavailableItems };
        }
      } else {
        return { success: false, error: 'Order has no items' };
      }
    } else {
      return { success: false, error: 'User is not verified' };
    }
  } else {
    return { success: false, error: 'User account is not active' };
  }
}

module.exports = { processOrder };
