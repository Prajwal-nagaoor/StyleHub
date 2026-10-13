import axios from 'axios';

export const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
export const api = axios.create({ baseURL: API_BASE, timeout: 15000 });
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('stylehub_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
export function messageFromError(error) {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((x) => x.msg).join(', ');
  if (typeof detail === 'string') return detail;
  if (error?.code === 'ECONNABORTED') return 'The server took too long to respond.';
  if (!error?.response) return 'Cannot connect to the StyleHub API. Start FastAPI and check the API URL.';
  return error.response.data?.message || `Request failed (${error.response.status}).`;
}
// These paths match the routes as they are currently defined in the supplied backend.
export const paths = {
  products: '/productview_product',
  productDetail: '/productget-product',
  cart: '/add-cartview-cart',
  addCart: '/add-cart/add-cart',
  updateCart: '/add-cart/update-cart',
  deleteCart: '/add-cart/delte-cart',
  orders: '/orderview_order',
  createOrder: '/order/create-order',
  cancelOrder: '/order/delete-order',
  paymentIntent: '/order/create-payment-intent',
};