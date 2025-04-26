import * as React from "react"
import { Drawer as DrawerPrimitive } from "vaadin-web-components"

import { cn } from "@/lib/utils"

const Drawer = ({
  className,
  ...props
}: React.ComponentProps<typeof DrawerPrimitive>) => (
  <DrawerPrimitive className={cn("fixed inset-0 z-50", className)} {...props} />
)
Drawer.displayName = "Drawer"

const DrawerTrigger = DrawerPrimitive.trigger

const DrawerClose = DrawerPrimitive.close

const DrawerContent = ({
  className,
  ...props
}: React.ComponentProps<typeof DrawerPrimitive.content>) => (
  <DrawerPrimitive.portal>
    <DrawerPrimitive.overlay className="fixed inset-0 z-50 bg-black/80" />
    <DrawerPrimitive.content
      className={cn(
        "fixed inset-x-0 bottom-0 z-50 mt-24 h-[85vh] rounded-t-[10px] bg-background",
        className
      )}
      {...props}
    />
  </DrawerPrimitive.portal>
)
DrawerContent.displayName = "DrawerContent"

const DrawerHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("px-4 pb-2 pt-4 grid gap-1.5", className)}
    {...props}
  />
)
DrawerHeader.displayName = "DrawerHeader"

const DrawerFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("px-4 py-4 mt-auto flex flex-col gap-2", className)}
    {...props}
  />
)
DrawerFooter.displayName = "DrawerFooter"

const DrawerTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
DrawerTitle.displayName = "DrawerTitle"

const DrawerDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
DrawerDescription.displayName = "DrawerDescription"

export {
  Drawer,
  DrawerTrigger,
  DrawerClose,
  DrawerContent,
  DrawerHeader,
  DrawerFooter,
  DrawerTitle,
  DrawerDescription,
}