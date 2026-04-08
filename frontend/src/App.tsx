import { Navigate, useRoutes } from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";
import SessionDetailPage from "./pages/SessionDetailPage";
import SessionsPage from "./pages/SessionsPage";
import RuntimeReviewDetailPage from "./pages/RuntimeReviewDetailPage";
import RuntimeReviewListPage from "./pages/RuntimeReviewListPage";

export default function App() {
  const element = useRoutes([
    {
      path: "/",
      element: <AppLayout />,
      children: [
        { index: true, element: <Navigate to="/sessions" replace /> },
        { path: "sessions", element: <SessionsPage /> },
        { path: "sessions/:sessionId", element: <SessionDetailPage /> },
        { path: "runtime-reviews", element: <RuntimeReviewListPage /> },
        { path: "runtime-reviews/:reviewId", element: <RuntimeReviewDetailPage /> }
      ]
    }
  ]);
  return element;
}
