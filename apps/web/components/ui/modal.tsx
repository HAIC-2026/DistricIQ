"use client";
import { useEffect, useRef } from "react";
export function Modal({
  children,
  className,
  labelId,
  onClose,
}: {
  children: React.ReactNode;
  className: string;
  labelId: string;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const callback = useRef(onClose);
  callback.current = onClose;
  useEffect(() => {
    const node = ref.current;
    const focused = document.activeElement as HTMLElement | null;
    if (node && !node.open) node.showModal();
    return () => {
      node?.close();
      focused?.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className={className}
      aria-labelledby={labelId}
      onCancel={(e) => {
        e.preventDefault();
        callback.current();
      }}
    >
      {children}
    </dialog>
  );
}
