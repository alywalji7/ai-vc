"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { InfoCircledIcon } from "@radix-ui/react-icons";

type Subscription = {
  id: string;
  tier: string;
  status: string;
  currentPeriodEnd: string;
  seats: {
    limit: number;
    used: number;
  };
  apiUsage: {
    daily: {
      limit: number;
      used: number;
    };
  };
};

type Invoice = {
  id: string;
  amount: number;
  currency: string;
  status: string;
  created: string;
  pdf: string;
};

export default function BillingSettingsPage() {
  const { data: session, status } = useSession();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [portalLoading, setPortalLoading] = useState(false);

  useEffect(() => {
    const fetchSubscriptionData = async () => {
      try {
        // Fetch subscription details
        const subscriptionRes = await fetch("/api/subscription");
        const subscriptionData = await subscriptionRes.json();
        setSubscription(subscriptionData);
        
        // Fetch invoice history
        const invoicesRes = await fetch("/api/invoices");
        const invoicesData = await invoicesRes.json();
        setInvoices(invoicesData);
      } catch (error) {
        console.error("Error fetching billing data:", error);
      } finally {
        setLoading(false);
      }
    };

    if (status === "authenticated") {
      fetchSubscriptionData();
    } else if (status === "unauthenticated") {
      setLoading(false);
    }
  }, [status]);

  const handleManageSubscription = async () => {
    setPortalLoading(true);
    try {
      const res = await fetch("/api/create-customer-portal", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      const { url } = await res.json();
      
      if (url) {
        window.location.href = url;
      }
    } catch (error) {
      console.error("Error opening customer portal:", error);
    } finally {
      setPortalLoading(false);
    }
  };

  // Format currency amount
  const formatCurrency = (amount: number, currency: string = "usd") => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency.toUpperCase(),
    }).format(amount);
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (status === "loading" || loading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-8 w-1/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <Separator />
        <div className="space-y-4">
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Billing & Subscription</h1>
        <p className="text-sm text-gray-600">
          Manage your subscription plan, payment methods, and billing history.
        </p>
      </div>
      
      <Separator />
      
      {subscription ? (
        <>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Current Plan</CardTitle>
                <Badge variant={subscription.status === "active" ? "default" : "destructive"}>
                  {subscription.status === "active" ? "Active" : subscription.status}
                </Badge>
              </div>
              <CardDescription>
                Your subscription renews on {formatDate(subscription.currentPeriodEnd)}
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-6">
              <div>
                <div className="text-sm font-medium">Plan</div>
                <div className="text-2xl font-bold mt-1 capitalize">{subscription.tier}</div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="text-sm font-medium">Seats</div>
                  <div className="text-lg">
                    <span className="font-bold">{subscription.seats.used}</span>
                    <span className="text-gray-600"> / {subscription.seats.limit === -1 ? 'Unlimited' : subscription.seats.limit}</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-sm font-medium">API Usage (Daily)</div>
                  <div className="text-lg">
                    <span className="font-bold">{subscription.apiUsage.daily.used}</span>
                    <span className="text-gray-600"> / {subscription.apiUsage.daily.limit}</span>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button onClick={handleManageSubscription} disabled={portalLoading}>
                {portalLoading ? "Loading..." : "Manage Subscription"}
              </Button>
            </CardFooter>
          </Card>
          
          {subscription.status === "canceled" && (
            <Alert variant="destructive">
              <InfoCircledIcon className="h-4 w-4" />
              <AlertTitle>Subscription Canceled</AlertTitle>
              <AlertDescription>
                Your subscription has been canceled and will not renew. You will have read-only access until the end of your billing period.
              </AlertDescription>
            </Alert>
          )}
          
          <div className="mt-8">
            <h2 className="text-xl font-bold mb-4">Billing History</h2>
            <div className="rounded-md border">
              <div className="grid grid-cols-4 p-4 bg-gray-50 font-medium">
                <div>Date</div>
                <div>Amount</div>
                <div>Status</div>
                <div className="text-right">Invoice</div>
              </div>
              {invoices.length > 0 ? (
                invoices.map((invoice) => (
                  <div key={invoice.id} className="grid grid-cols-4 p-4 border-t">
                    <div>{formatDate(invoice.created)}</div>
                    <div>{formatCurrency(invoice.amount, invoice.currency)}</div>
                    <div className="capitalize">{invoice.status}</div>
                    <div className="text-right">
                      <a 
                        href={invoice.pdf} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        View
                      </a>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-4 border-t text-center text-gray-600">
                  No invoices found
                </div>
              )}
            </div>
          </div>
        </>
      ) : (
        <Alert>
          <InfoCircledIcon className="h-4 w-4" />
          <AlertTitle>No Active Subscription</AlertTitle>
          <AlertDescription>
            You don't have an active subscription. Please visit the pricing page to subscribe.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}