import { fireEvent, render, screen } from "@testing-library/react-native";
import { Button, ClassBadge } from "@/components/ui";
import { CLASS_META } from "@/theme/classes";
import type { ClassId } from "@/types";

describe("ClassBadge", () => {
  it.each([1, 2, 3, 4, 5, 6] as ClassId[])("class %i shows its text label (not colour alone)", async (c) => {
    await render(<ClassBadge cls={c} />);
    expect(screen.getByText(CLASS_META[c].label)).toBeTruthy();
  });
});

describe("Button", () => {
  it("fires onPress", async () => {
    const fn = jest.fn();
    await render(<Button label="Go" onPress={fn} />);
    await fireEvent.press(screen.getByRole("button", { name: "Go" }));
    expect(fn).toHaveBeenCalledTimes(1);
  });
  it("does not fire when disabled", async () => {
    const fn = jest.fn();
    await render(<Button label="Go" onPress={fn} disabled />);
    await fireEvent.press(screen.getByRole("button", { name: "Go" }));
    expect(fn).not.toHaveBeenCalled();
  });
});
