import { render, screen } from '@testing-library/react';
import App from './App';

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
