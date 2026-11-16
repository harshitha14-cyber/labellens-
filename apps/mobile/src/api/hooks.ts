import { useQuery } from "@tanstack/react-query";
import { api } from "./mockApi";

export const useCategories = () => useQuery({ queryKey: ["categories"], queryFn: api.categories });
export const useScans = () => useQuery({ queryKey: ["scans"], queryFn: api.scans });
export const useScan = (id: string) => useQuery({ queryKey: ["scan", id], queryFn: () => api.scan(id) });
export const useIngredient = (id: string) => useQuery({ queryKey: ["ingredient", id], queryFn: () => api.ingredient(id) });
export const useIngredients = () => useQuery({ queryKey: ["ingredients"], queryFn: api.ingredients });
export const useAlternatives = () => useQuery({ queryKey: ["alternatives"], queryFn: api.alternatives });
