import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import {
  Button, Card, CardHeader, Field, Input, Select, Spinner, Tab, TabList, Textarea,
} from "@fluentui/react-components";
import { Link, Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";
import { api, browseRequests, myTrips, requestDetails, setSessionToken, signIn, signUp } from "./api/client";
import { copy } from "./i18n";
import type { Language } from "./i18n";
import type { Account, DriverApplication, Offer, RideRequest, Trip } from "./types";

type Session = {
  user: Account | null;
  lang: Language;
  setLang: (lang: Language) => void;
  authenticate: (account: Account, token: string) => void;
  signOut: () => void;
  t: (key: string) => string;
};
const SessionContext = createContext<Session | null>(null);

function useSession() {
  const context = useContext(SessionContext);
  if (!context) throw new Error("Session context is missing.");
  return context;
}

function App() {
  const [user, setUser] = useState<Account | null>(null);
  const [lang, setLang] = useState<Language>("ar");
  const session = useMemo<Session>(() => ({
    user, lang, setLang,
    authenticate: (account, token) => { setSessionToken(token); setUser(account); setLang(account.preferredLanguage); },
    signOut: () => { setSessionToken(null); setUser(null); },
    t: (key) => copy[lang][key] ?? key,
  }), [user, lang]);

  return (
    <SessionContext.Provider value={session}>
      <div className="app-shell" dir={lang === "ar" ? "rtl" : "ltr"} lang={lang}>
        {user && <AppHeader />}
        <main className={user ? "main-content" : "auth-content"}>
          <Routes>
            <Route path="/login" element={user ? <Navigate to="/" replace /> : <AuthPage />} />
            <Route path="/register" element={user ? <Navigate to="/" replace /> : <AuthPage register />} />
            <Route path="*" element={user ? <ProtectedRoutes /> : <Navigate to="/login" replace />} />
          </Routes>
        </main>
        <footer className="site-footer">{lang === "ar" ? "وصلة · نموذج محلي قابل للاختبار" : "Wasla · Local testable MVP"}</footer>
      </div>
    </SessionContext.Provider>
  );
}

function AppHeader() {
  const { user, lang, setLang, signOut, t } = useSession();
  const navigate = useNavigate();
  return (
    <header className="topbar">
      <Link to="/" className="brand-lockup" aria-label={t("brand")}>
        <span className="brand-mark" aria-hidden="true">و</span>
        <span><strong>{t("brand")}</strong><small>{t("tagline")}</small></span>
      </Link>
      <nav className="main-nav" aria-label={t("marketplace")}>
        <Link to="/">{t("marketplace")}</Link>
        <Link to="/requests/new">{t("newRequest")}</Link>
        <Link to="/trips">{t("myTrips")}</Link>
        <Link to="/drivers/apply">{t("driver")}</Link>
        {user?.role === "operator" && <Link to="/operations/review">{t("operations")}</Link>}
      </nav>
      <div className="topbar-actions">
        <Button appearance="subtle" onClick={() => setLang(lang === "ar" ? "en" : "ar")}>{t("chooseLanguage")}</Button>
        <span className="user-chip">{user?.displayName}</span>
        <Button appearance="secondary" onClick={() => { signOut(); navigate("/login"); }}>{t("signOut")}</Button>
      </div>
    </header>
  );
}

function ProtectedRoutes() {
  return <Routes>
    <Route path="/" element={<MarketplacePage />} />
    <Route path="/requests/new" element={<CreateRequestPage />} />
    <Route path="/requests/:id" element={<RequestDetailsPage />} />
    <Route path="/drivers/apply" element={<DriverApplicationPage />} />
    <Route path="/trips" element={<TripsPage />} />
    <Route path="/operations/review" element={<OperationsPage />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>;
}

function AuthPage({ register = false }: { register?: boolean }) {
  const { t, lang, setLang, authenticate } = useSession();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setBusy(true);
    const form = new FormData(event.currentTarget);
    try {
      const result = register ? await signUp({
        displayName: String(form.get("displayName")),
        email: String(form.get("email")),
        phone: String(form.get("phone") ?? ""),
        password: String(form.get("password")),
        preferredLanguage: lang,
        accountType: form.get("accountType") as "individual" | "business",
      }) : await signIn(String(form.get("email")), String(form.get("password")));
      authenticate(result.account, result.accessToken);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : t("errorTitle"));
    } finally { setBusy(false); }
  }
  return (
    <section className="auth-layout">
      <div className="auth-story">
        <div className="brand-mark large" aria-hidden="true">و</div>
        <span className="eyebrow">{t("brand")} · EGYPT</span>
        <h1>{t("tagline")}</h1>
        <p>{t("subtitle")}</p>
        <div className="route-decoration"><span>القاهرة</span><i /><span>الإسكندرية</span></div>
      </div>
      <Card className="auth-card">
        <div className="auth-language"><Button appearance="subtle" onClick={() => setLang(lang === "ar" ? "en" : "ar")}>{t("chooseLanguage")}</Button></div>
        <h2>{register ? t("createAccount") : t("welcome")}</h2>
        <p className="muted">{t("loginHint")}</p>
        <form onSubmit={submit} className="form-stack">
          {register && <>
            <Field label={t("displayName")} required><Input name="displayName" autoComplete="name" required minLength={2} maxLength={100} /></Field>
            <Field label={t("phone")}><Input name="phone" type="tel" autoComplete="tel" /></Field>
            <Field label={t("accountType")} required>
              <Select name="accountType" defaultValue="individual">
                <option value="individual">{t("individual")}</option>
                <option value="business">{t("business")}</option>
              </Select>
            </Field>
          </>}
          <Field label={t("email")} required><Input name="email" type="email" autoComplete="email" required maxLength={254} /></Field>
          <Field label={t("password")} hint={register ? t("passwordHint") : undefined} required>
            <Input name="password" type="password" autoComplete={register ? "new-password" : "current-password"} required minLength={register ? 12 : 1} maxLength={128} />
          </Field>
          {error && <ErrorBanner>{error}</ErrorBanner>}
          <Button type="submit" appearance="primary" size="large" disabled={busy}>
            {busy ? <Spinner size="tiny" /> : register ? t("createAccount") : t("signIn")}
          </Button>
        </form>
        <p className="switch-auth">
          {register ? t("alreadyAccount") : t("noAccount")}{" "}
          <Link to={register ? "/login" : "/register"}>{register ? t("signIn") : t("createAccount")}</Link>
        </p>
      </Card>
    </section>
  );
}

function MarketplacePage() {
  const { t } = useSession();
  const [filter, setFilter] = useState("");
  const [rows, setRows] = useState<RideRequest[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    setLoading(true);
    browseRequests(filter).then((result) => { if (active) setRows(result.requests); })
      .catch((err) => { if (active) setError(err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [filter]);
  return <section>
    <div className="page-heading">
      <div><span className="eyebrow">WASLA MARKETPLACE</span><h1>{t("requestsTitle")}</h1><p>{t("subtitle")}</p></div>
      <Button as={Link} to="/requests/new" appearance="primary">{t("newRequest")}</Button>
    </div>
    <TabList selectedValue={filter || "all"} onTabSelect={(_e, data) => setFilter(data.value === "all" ? "" : String(data.value))}>
      <Tab value="all">{t("all")}</Tab><Tab value="passenger">{t("passenger")}</Tab><Tab value="freight">{t("freight")}</Tab>
    </TabList>
    {error && <ErrorBanner>{error}</ErrorBanner>}
    {loading ? <div className="loading"><Spinner label={t("loading")} /></div> : rows.length === 0 ?
      <EmptyState>{t("noRequests")}</EmptyState> :
      <div className="request-grid">{rows.map((request) => <RequestCard key={request.id} request={request} />)}</div>}
  </section>;
}

function RequestCard({ request }: { request: RideRequest }) {
  const { t, lang } = useSession();
  return <Card className="request-card">
    <div className="card-kicker"><span className={`service-badge ${request.serviceType}`}>{request.serviceType === "passenger" ? t("passenger") : t("freight")}</span><span>{t("cashOnly")}</span></div>
    <h3>{request.origin ?? t("unknown")} <span className="route-arrow">←</span> {request.destination ?? t("unknown")}</h3>
    <p>{request.details}</p>
    <dl className="request-meta">
      <div><dt>{t("when")}</dt><dd>{formatDate(request.schedule.scheduledAt, lang)}</dd></div>
      <div><dt>{t("preferredFare")}</dt><dd className="fare">{formatMoney(request.preferredFare, lang)}</dd></div>
    </dl>
    <div className="card-footer"><span>{request.offerCount} {t("offerCount")}</span><Button as={Link} to={`/requests/${request.id}`} appearance="secondary">{t("view")}</Button></div>
  </Card>;
}

function CreateRequestPage() {
  const { t } = useSession();
  const navigate = useNavigate();
  const [type, setType] = useState<"passenger" | "freight">("passenger");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setBusy(true);
    const form = new FormData(event.currentTarget);
    try {
      const result = await api<{ request: RideRequest }>("/api/requests", {
        method: "POST",
        body: JSON.stringify({
          serviceType: type, origin: form.get("origin"), destination: form.get("destination"),
          schedule: { scheduledAt: form.get("scheduledAt") }, details: form.get("details"),
          preferredFare: Number(form.get("preferredFare")), paymentMethod: "cash",
        }),
      });
      navigate(`/requests/${result.request.id}`);
    } catch (err) { setError(err instanceof Error ? err.message : t("errorTitle")); }
    finally { setBusy(false); }
  }
  return <PageForm title={t("createTitle")} onSubmit={submit} error={error} busy={busy} submitLabel={t("publish")}>
    <Field label={t("serviceType")} required>
      <Select value={type} onChange={(e) => setType(e.target.value as "passenger" | "freight")}>
        <option value="passenger">{t("passenger")}</option><option value="freight">{t("freight")}</option>
      </Select>
    </Field>
    <div className="form-row">
      <Field label={t("origin")} required><Input name="origin" required minLength={2} maxLength={160} /></Field>
      <Field label={t("destination")} required><Input name="destination" required minLength={2} maxLength={160} /></Field>
    </div>
    <div className="form-row">
      <Field label={t("scheduledAt")} required><Input name="scheduledAt" type="datetime-local" required /></Field>
      <Field label={t("fare")} required><Input name="preferredFare" type="number" min="1" max="1000000" step="1" placeholder={t("fareExample")} required /></Field>
    </div>
    <Field label={t("details")} required><Textarea name="details" rows={3} maxLength={1000} placeholder={type === "passenger" ? t("passengerDetails") : t("freightDetails")} required /></Field>
    <p className="inline-note">{t("cashOnly")}</p>
  </PageForm>;
}

function RequestDetailsPage() {
  const { id = "" } = useParams();
  const { t, user, lang } = useSession();
  const [data, setData] = useState<{ request: RideRequest; offers: Offer[]; trip: Trip | null } | null>(null);
  const [error, setError] = useState("");
  const [offerError, setOfferError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const refresh = () => requestDetails(id).then(setData).catch((err) => setError(err.message));
  useEffect(() => { void refresh(); }, [id]);
  async function offer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setOfferError(""); setBusy(true);
    const form = new FormData(event.currentTarget);
    try {
      await api(`/api/requests/${id}/offers`, { method: "POST", body: JSON.stringify({
        fare: Number(form.get("fare")), etaMinutes: Number(form.get("etaMinutes")), message: form.get("message"),
      }) });
      await refresh();
    } catch (err) { setOfferError(err instanceof Error ? err.message : t("errorTitle")); }
    finally { setBusy(false); }
  }
  async function accept(offerId: string) {
    try { await api(`/api/requests/${id}/offers/${offerId}/accept`, { method: "POST" }); navigate("/trips"); }
    catch (err) { setError(err instanceof Error ? err.message : t("errorTitle")); }
  }
  if (error) return <ErrorBanner>{error}</ErrorBanner>;
  if (!data) return <div className="loading"><Spinner label={t("loading")} /></div>;
  const owner = user?.id === data.request.ownerId;
  return <section>
    <Button appearance="subtle" onClick={() => navigate(-1)}>← {t("back")}</Button>
    <div className="detail-layout">
      <Card className="detail-main">
        <span className={`service-badge ${data.request.serviceType}`}>{data.request.serviceType === "passenger" ? t("passenger") : t("freight")}</span>
        <h1>{data.request.origin} <span className="route-arrow">←</span> {data.request.destination}</h1>
        <p>{data.request.details}</p>
        <dl className="request-meta">
          <div><dt>{t("when")}</dt><dd>{formatDate(data.request.schedule.scheduledAt, lang)}</dd></div>
          <div><dt>{t("preferredFare")}</dt><dd className="fare">{formatMoney(data.request.preferredFare, lang)}</dd></div>
        </dl>
        {data.trip && <div className="inline-note">{t("tripStatus")}: {t(data.trip.status)}</div>}
      </Card>
      <section className="offers-column">
        <h2>{t("offersTitle")} <span className="count-pill">{data.offers.length}</span></h2>
        {data.offers.length === 0 ? <EmptyState>{t("noRequests")}</EmptyState> : data.offers.map((item) =>
          <Card key={item.id} className="offer-card">
            <div className="offer-top"><strong>{item.driverName}</strong><strong className="fare">{formatMoney(item.fare, lang)}</strong></div>
            <div className="offer-sub">{item.etaMinutes} {t("eta")}{item.message ? ` · ${item.message}` : ""}</div>
            {owner && data.request.status === "open" && <Button appearance="primary" onClick={() => accept(item.id)}>{t("choose")}</Button>}
          </Card>)}
        {user?.role === "driver" && data.request.status === "open" && !owner &&
          <Card className="offer-form-card"><h3>{t("sendOffer")}</h3>
            <form className="form-stack" onSubmit={offer}>
              <Field label={t("offerFare")} required><Input name="fare" type="number" min="1" step="1" required /></Field>
              <Field label={t("eta")} required><Input name="etaMinutes" type="number" min="1" max="1440" required /></Field>
              <Field label={t("message")}><Input name="message" maxLength={500} /></Field>
              {offerError && <ErrorBanner>{offerError}</ErrorBanner>}
              <Button appearance="primary" type="submit" disabled={busy}>{t("sendOffer")}</Button>
            </form>
          </Card>}
      </section>
    </div>
  </section>;
}

function DriverApplicationPage() {
  const { t } = useSession();
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setBusy(true);
    const form = new FormData(event.currentTarget);
    try {
      await api("/api/drivers/applications", { method: "POST", body: JSON.stringify({
        profile: { homeCity: form.get("homeCity") },
        vehicle: { type: form.get("vehicleType"), make: form.get("vehicleMake"),
          year: Number(form.get("vehicleYear")), passengerSeats: form.get("seats") || undefined,
          freightCapacityKg: form.get("capacity") || undefined },
      }) });
      setSuccess(true);
    } catch (err) { setError(err instanceof Error ? err.message : t("errorTitle")); }
    finally { setBusy(false); }
  }
  if (success) return <section className="narrow"><div className="success-panel"><span className="success-icon">✓</span><h1>{t("applicationSuccess")}</h1><p>{t("applicationPending")}</p></div></section>;
  return <PageForm title={t("applicationTitle")} onSubmit={submit} error={error} busy={busy} submitLabel={t("submitApplication")}>
    <p className="muted">{t("applicationPending")}</p>
    <Field label={t("homeCity")} required><Input name="homeCity" minLength={2} maxLength={100} required /></Field>
    <div className="form-row">
      <Field label={t("vehicleType")} required><Input name="vehicleType" minLength={2} maxLength={80} required /></Field>
      <Field label={t("vehicleMake")} required><Input name="vehicleMake" minLength={2} maxLength={80} required /></Field>
    </div>
    <div className="form-row">
      <Field label={t("vehicleYear")} required><Input name="vehicleYear" type="number" min="1980" max="2100" required /></Field>
      <Field label={t("seats")}><Input name="seats" type="number" min="1" max="50" /></Field>
    </div>
    <Field label={t("capacity")}><Input name="capacity" type="number" min="1" step="1" /></Field>
    <p className="inline-note">{t("applicationPending")}</p>
  </PageForm>;
}

function TripsPage() {
  const { t, user, lang } = useSession();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [error, setError] = useState("");
  const reload = () => myTrips().then((result) => setTrips(result.trips)).catch((err) => setError(err.message));
  useEffect(() => { void reload(); }, []);
  async function update(trip: Trip, status?: Trip["status"], cashSettlementStatus?: "pending" | "settled") {
    setError("");
    try {
      await api(`/api/trips/${trip.id}`, { method: "PATCH", body: JSON.stringify({ status, cashSettlementStatus }) });
      await reload();
    } catch (err) { setError(err instanceof Error ? err.message : t("errorTitle")); }
  }
  return <section>
    <div className="page-heading"><div><span className="eyebrow">WASLA</span><h1>{t("tripsTitle")}</h1></div></div>
    {error && <ErrorBanner>{error}</ErrorBanner>}
    {trips.length === 0 ? <EmptyState>{t("emptyTrips")}</EmptyState> :
      <div className="trip-list">{trips.map((trip) => <TripCard key={trip.id} trip={trip} lang={lang} user={user} onUpdate={update} />)}</div>}
  </section>;
}

function TripCard({ trip, lang, user, onUpdate }: {
  trip: Trip; lang: Language; user: Account | null;
  onUpdate: (trip: Trip, status?: Trip["status"], settlement?: "pending" | "settled") => void;
}) {
  const { t } = useSession();
  const [reportMsg, setReportMsg] = useState("");
  const [ratingMsg, setRatingMsg] = useState("");
  const [error, setError] = useState("");
  const [showReport, setShowReport] = useState(false);
  const [showRating, setShowRating] = useState(false);
  const [busy, setBusy] = useState(false);
  async function submitReport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    const form = new FormData(event.currentTarget);
    try {
      await api(`/api/trips/${trip.id}/reports`, { method: "POST", body: JSON.stringify({
        category: form.get("category"), description: form.get("description"),
      }) }); setReportMsg(t("submitReport")); setShowReport(false);
    } catch (err) { setError(err instanceof Error ? err.message : t("errorTitle")); }
    finally { setBusy(false); }
  }
  async function submitRating(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    const form = new FormData(event.currentTarget);
    try {
      await api(`/api/trips/${trip.id}/ratings`, { method: "POST", body: JSON.stringify({
        score: Number(form.get("score")), comment: form.get("comment"),
      }) }); setRatingMsg(t("submitRating")); setShowRating(false);
    } catch (err) { setError(err instanceof Error ? err.message : t("errorTitle")); }
    finally { setBusy(false); }
  }
  const nextStatus: Partial<Record<Trip["status"], Trip["status"]>> = {
    accepted: "driver_en_route", driver_en_route: "in_progress", in_progress: "completed",
  };
  return <Card className="trip-card">
    <div className="trip-header"><div><span className="eyebrow">{t("tripStatus")}</span><h3>{t(trip.status)}</h3></div><span className={`status-pill status-${trip.status}`}>{t(trip.status)}</span></div>
    <div className="trip-route"><span>{t("requestDetail")}</span><code>{trip.requestId.slice(0, 8)}</code><span>{formatMoney(0, lang) === "٠ ج.م.‏" ? "نقداً" : "Cash"}</span></div>
    {error && <ErrorBanner>{error}</ErrorBanner>}
    <div className="trip-actions">
      {user?.role === "driver" && nextStatus[trip.status] && <Button appearance="primary" onClick={() => onUpdate(trip, nextStatus[trip.status])}>{t("advanceTrip")}: {t(nextStatus[trip.status]!)}</Button>}
      {trip.status === "completed" && trip.cashSettlementStatus !== "settled" &&
        <Button appearance="secondary" onClick={() => onUpdate(trip, undefined, "settled")}>{t("settle")}</Button>}
      {trip.status !== "cancelled" && <Button appearance="subtle" onClick={() => setShowReport((value) => !value)}>{t("support")}</Button>}
      {trip.status === "completed" && <Button appearance="subtle" onClick={() => setShowRating((value) => !value)}>{t("rateTrip")}</Button>}
      {trip.cashSettlementStatus === "settled" && <span className="success-text">✓ {t("settled")}</span>}
    </div>
    {showReport && <form className="inline-form" onSubmit={submitReport}>
      <Field label={t("reportCategory")} required><Select name="category"><option value="service">{t("service")}</option><option value="safety">{t("safety")}</option><option value="payment">{t("payment")}</option><option value="other">{t("other")}</option></Select></Field>
      <Field label={t("reportDescription")} required><Textarea name="description" rows={3} minLength={10} maxLength={2000} required /></Field>
      <p className="muted small">{t("noEmergency")}</p><Button type="submit" appearance="primary" disabled={busy}>{t("submitReport")}</Button>
    </form>}
    {showRating && <form className="inline-form" onSubmit={submitRating}>
      <Field label={t("score")} required><Select name="score" defaultValue="5"><option value="5">5</option><option value="4">4</option><option value="3">3</option><option value="2">2</option><option value="1">1</option></Select></Field>
      <Field label={t("comment")}><Input name="comment" maxLength={1000} /></Field>
      <Button type="submit" appearance="primary" disabled={busy}>{t("submitRating")}</Button>
    </form>}
    {(reportMsg || ratingMsg) && <p className="success-text">{reportMsg || ratingMsg}</p>}
  </Card>;
}

function OperationsPage() {
  const { t } = useSession();
  const [apps, setApps] = useState<DriverApplication[]>([]);
  const [reports, setReports] = useState<Array<{ id: string; category: string; description: string; tripId: string }>>([]);
  const [error, setError] = useState("");
  const refresh = async () => {
    try {
      const [applications, support] = await Promise.all([
        api<{ applications: DriverApplication[] }>("/api/operations/driver-applications"),
        api<{ reports: typeof reports }>("/api/operations/support-reports"),
      ]);
      setApps(applications.applications); setReports(support.reports);
    } catch (err) { setError(err instanceof Error ? err.message : t("errorTitle")); }
  };
  useEffect(() => { void refresh(); }, []);
  async function decide(id: string, decision: "approved" | "rejected") {
    const notes = window.prompt(t("reviewNote")) ?? "";
    try {
      await api(`/api/operations/driver-applications/${id}`, {
        method: "PATCH", body: JSON.stringify({ decision, notes }),
      });
      await refresh();
    } catch (err) { setError(err instanceof Error ? err.message : t("errorTitle")); }
  }
  return <section>
    <div className="page-heading"><div><span className="eyebrow">WASLA · OPERATIONS</span><h1>{t("reviewTitle")}</h1></div></div>
    {error && <ErrorBanner>{error}</ErrorBanner>}
    <div className="operations-grid">
      <section><h2>{t("reviewTitle")}</h2>{apps.length === 0 ? <EmptyState>{t("noApplications")}</EmptyState> :
        apps.map((item) => <Card key={item.id} className="application-card">
          <div className="offer-top"><strong>{item.displayName}</strong><span className={`status-pill status-${item.status}`}>{t(item.status)}</span></div>
          <p>{item.homeCity} · {item.vehicleType} · {item.vehicleMake} {item.vehicleYear}</p>
          {item.status === "pending" && <div className="trip-actions">
            <Button appearance="primary" onClick={() => decide(item.id, "approved")}>{t("approve")}</Button>
            <Button appearance="secondary" onClick={() => decide(item.id, "rejected")}>{t("reject")}</Button>
          </div>}
        </Card>)}</section>
      <section><h2>{t("support")}</h2>{reports.length === 0 ? <EmptyState>{t("noApplications")}</EmptyState> :
        reports.map((report) => <Card key={report.id} className="application-card">
          <strong>{t(report.category)} · {report.tripId.slice(0, 8)}</strong><p>{report.description}</p>
        </Card>)}</section>
    </div>
  </section>;
}

function PageForm({ title, children, onSubmit, error, busy, submitLabel }: {
  title: string; children: ReactNode; onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  error: string; busy: boolean; submitLabel: string;
}) {
  const navigate = useNavigate();
  const { t } = useSession();
  return <section className="narrow">
    <Button appearance="subtle" onClick={() => navigate(-1)}>← {t("back")}</Button>
    <Card className="form-card"><span className="eyebrow">WASLA</span><h1>{title}</h1>
      <form className="form-stack" onSubmit={onSubmit}>
        {children}
        {error && <ErrorBanner>{error}</ErrorBanner>}
        <Button type="submit" appearance="primary" size="large" disabled={busy}>{busy ? <Spinner size="tiny" /> : submitLabel}</Button>
      </form>
    </Card>
  </section>;
}

function ErrorBanner({ children }: { children: ReactNode }) {
  return <div className="error-banner" role="alert"><strong>!</strong><span>{children}</span></div>;
}
function EmptyState({ children }: { children: ReactNode }) {
  return <div className="empty-state"><span className="empty-icon">⌁</span><p>{children}</p></div>;
}
function formatMoney(value: number, lang: Language) {
  return new Intl.NumberFormat(lang === "ar" ? "ar-EG" : "en-EG", {
    style: "currency", currency: "EGP", maximumFractionDigits: 0,
  }).format(value);
}
function formatDate(value: string, lang: Language) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(lang === "ar" ? "ar-EG" : "en-EG", {
    dateStyle: "medium", timeStyle: "short",
  }).format(date);
}

export default App;
