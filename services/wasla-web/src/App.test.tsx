import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

const apiMocks = vi.hoisted(() => ({
  api: vi.fn(),
  browseRequests: vi.fn(),
  myTrips: vi.fn(),
  requestDetails: vi.fn(),
  setSessionToken: vi.fn(),
  signIn: vi.fn(),
  signUp: vi.fn(),
}));

vi.mock("./api/client", () => apiMocks);

function deferred<Value>() {
  let resolvePromise!: (value: Value) => void;
  const promise = new Promise<Value>((resolve) => {
    resolvePromise = resolve;
  });
  return { promise, resolve: resolvePromise };
}

async function signInAndOpenTrips() {
  fireEvent.click(screen.getByRole("button", { name: "English" }));
  fireEvent.change(screen.getByLabelText(/Email address/), {
    target: { value: "customer@example.test" },
  });
  fireEvent.change(screen.getByLabelText(/Password/), {
    target: { value: "test-password" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

  await screen.findByRole("heading", { name: "Open transport requests" });
  fireEvent.click(screen.getByRole("link", { name: "My trips" }));
}

describe("trips screen", () => {
  afterEach(cleanup);

  beforeEach(() => {
    vi.clearAllMocks();
    apiMocks.browseRequests.mockResolvedValue({ requests: [], total: 0 });
    apiMocks.signIn.mockResolvedValue({
      account: {
        id: "account-1",
        displayName: "Test customer",
        email: "customer@example.test",
        preferredLanguage: "en",
        accountType: "individual",
        role: "customer",
      },
      accessToken: "test-token",
    });
  });

  it("shows loading feedback before displaying an empty trips state", async () => {
    const trips = deferred<{ trips: [] }>();
    apiMocks.myTrips.mockReturnValue(trips.promise);
    render(<MemoryRouter><App /></MemoryRouter>);
    await signInAndOpenTrips();

    expect(await screen.findByRole("status", { name: "Loading…" })).toBeInTheDocument();
    expect(screen.queryByText("Accepted trips will appear here.")).not.toBeInTheDocument();

    trips.resolve({ trips: [] });
    expect(await screen.findByText("Accepted trips will appear here.")).toBeInTheDocument();
  });

  it("lets users retry after a trips request fails", async () => {
    apiMocks.myTrips
      .mockRejectedValueOnce(new Error("Service unavailable"))
      .mockResolvedValueOnce({ trips: [] });
    render(<MemoryRouter><App /></MemoryRouter>);
    await signInAndOpenTrips();

    expect(await screen.findByRole("alert")).toHaveTextContent("Service unavailable");
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));

    expect(await screen.findByText("Accepted trips will appear here.")).toBeInTheDocument();
  });
});