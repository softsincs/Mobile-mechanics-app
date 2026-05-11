import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  createRootRouteWithContext,
  useRouter,
  useRouterState,
  HeadContent,
  Scripts,
  Link,
} from "@tanstack/react-router";
import { Toaster } from "sonner";

import appCss from "../styles.css?url";
import { Header } from "@/components/site/Header";
import { Footer } from "@/components/site/Footer";

function NotFoundComponent() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-gradient-primary">404</h1>
        <h2 className="mt-4 text-xl font-semibold">Page not found</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          to="/"
          className="mt-6 inline-flex items-center justify-center rounded-md bg-gradient-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
        >
          Go home
        </Link>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  return (
    <div className="flex min-h-[70vh] items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-xl font-semibold">Something went wrong</h1>
        <p className="mt-2 text-sm text-muted-foreground">{error.message}</p>
        <button
          onClick={() => { router.invalidate(); reset(); }}
          className="mt-6 inline-flex items-center justify-center rounded-md bg-gradient-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
        >
          Try again
        </button>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "MobileMechanic — On-demand car care, at your driveway" },
      {
        name: "description",
        content:
          "Book certified mobile mechanics on-demand. Live tracking, transparent pricing, secure payments. Premium car care for modern drivers.",
      },
      { property: "og:title", content: "MobileMechanic — On-demand car care, at your driveway" },
      { property: "og:description", content: "Mobile Mechanic Hub is a comprehensive platform for booking car maintenance and mechanic services." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:title", content: "MobileMechanic — On-demand car care, at your driveway" },
      { name: "description", content: "Mobile Mechanic Hub is a comprehensive platform for booking car maintenance and mechanic services." },
      { name: "twitter:description", content: "Mobile Mechanic Hub is a comprehensive platform for booking car maintenance and mechanic services." },
      { property: "og:image", content: "https://pub-bb2e103a32db4e198524a2e9ed8f35b4.r2.dev/266a2cc6-d012-40ec-903c-51fd05e25795/id-preview-d7007f4c--e2663856-ffe1-49fb-b709-ae91b4c06e1e.lovable.app-1778231561727.png" },
      { name: "twitter:image", content: "https://pub-bb2e103a32db4e198524a2e9ed8f35b4.r2.dev/266a2cc6-d012-40ec-903c-51fd05e25795/id-preview-d7007f4c--e2663856-ffe1-49fb-b709-ae91b4c06e1e.lovable.app-1778231561727.png" },
    ],
    links: [{ rel: "stylesheet", href: appCss }],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  const path = useRouterState({ select: (s) => s.location.pathname });
  const isAuth = path === "/login" || path === "/signup";

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex min-h-screen flex-col bg-background text-foreground">
        {!isAuth && <Header />}
        <main className="flex-1">
          <Outlet />
        </main>
        {!isAuth && <Footer />}
      </div>
      <Toaster richColors position="top-right" />
    </QueryClientProvider>
  );
}
