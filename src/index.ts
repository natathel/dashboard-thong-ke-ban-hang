type Order = {
  channel: 'website' | 'facebook' | 'shopee';
  revenue: number;
};

const orders: Order[] = [
  { channel: 'website', revenue: 1250000 },
  { channel: 'facebook', revenue: 860000 },
  { channel: 'shopee', revenue: 1420000 },
  { channel: 'website', revenue: 730000 },
];

const summary = orders.reduce<Record<string, number>>((acc, order) => {
  acc[order.channel] = (acc[order.channel] || 0) + order.revenue;
  return acc;
}, {});

console.log('DASHBOARD THỐNG KÊ BÁN HÀNG');
console.table(summary);
