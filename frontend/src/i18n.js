export const translations = {
  en: {
    title: 'PayPal AI Prototype',
    chat: 'Chat',
    extract: 'Extract',
    createInvoice: 'Create Invoice',
    dashboard: 'Dashboard',
    billed: 'Billed',
    paid: 'Paid',
    pending: 'Pending',
    avgDays: 'Avg days to pay',
    topClients: 'Top clients',
    revenueByMonth: 'Revenue by month',
    pdf: 'PDF',
  },
  es: {
    title: 'Prototipo PayPal AI',
    chat: 'Chat',
    extract: 'Extraer',
    createInvoice: 'Crear Factura',
    dashboard: 'Panel',
    billed: 'Facturado',
    paid: 'Cobrado',
    pending: 'Pendiente',
    avgDays: 'Días promedio de cobro',
    topClients: 'Mejores clientes',
    revenueByMonth: 'Ingresos por mes',
    pdf: 'PDF',
  },
}

export function t(lang, key) {
  return (translations[lang] && translations[lang][key]) || key
}