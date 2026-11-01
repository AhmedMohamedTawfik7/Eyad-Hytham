export type Account = {
  id: string;
  displayName: string;
  email: string;
  phone?: string | null;
  preferredLanguage: "ar" | "en";
  accountType: "individual" | "business";
  role: "customer" | "driver" | "operator";
};

export type RideRequest = {
  id: string;
  ownerId: string;
  ownerName: string;
  serviceType: "passenger" | "freight";
  origin: string | null;
  destination: string | null;
  schedule: { scheduledAt: string };
  details: string;
  preferredFare: number;
  paymentMethod: "cash";
  status: string;
  offerCount: number;
};

export type Offer = {
  id: string;
  requestId: string;
  driverId: string;
  driverName: string;
  fare: number;
  message: string;
  etaMinutes: number;
  status: string;
};

export type Trip = {
  id: string;
  requestId: string;
  offerId: string;
  status: "accepted" | "driver_en_route" | "in_progress" | "completed" | "cancelled";
  cashSettlementStatus: "pending" | "settled";
};

export type DriverApplication = {
  id: string;
  displayName: string;
  homeCity: string;
  vehicleType: string;
  vehicleMake: string;
  vehicleYear: number;
  passengerSeats?: number | null;
  freightCapacityKg?: number | null;
  status: string;
};

export type ApiError = { error: { code: string; message: string; details?: unknown } };
