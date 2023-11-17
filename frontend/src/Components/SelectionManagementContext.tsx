import {createContext, PropsWithChildren, useContext, useState} from "react";

type Selectable = string | { url: string }

export interface ISelectionManagementContext {
    resource_urls: string[]
    select: (resource: Selectable) => void
    deselect: (resource: Selectable) => void
    setSelected: (resource: Selectable, selected: boolean) => void
    toggleSelected: (resource: Selectable) => void
    isSelected: (resource: Selectable) => boolean
    clearSelections: () => void
}

const SelectionManagementContext = createContext({} as ISelectionManagementContext)

export const useSelectionManagement = () => {
    const context = useContext(SelectionManagementContext) as ISelectionManagementContext
    if (context === undefined) {
        throw new Error('useSelectionManagement must be used within a SelectionManagementContextProvider')
    }
    return context
}

export default function SelectionManagementContextProvider({children}: PropsWithChildren<{}>) {
    const [selected, setSelected] = useState<string[]>([])

    const to_url = (resource: Selectable) => typeof resource === 'string' ? resource : resource.url
    const select = (resource: Selectable) => {
        setSelected([...selected, to_url(resource)])
    }
    const deselect = (resource: Selectable) => {
        setSelected(selected.filter(x => x !== to_url(resource)))
    }
    const isSelected = (resource: Selectable) => selected.includes(to_url(resource))
    const toggleSelected = (resource: Selectable) => isSelected(resource) ? deselect(resource) : select(resource)

    return <SelectionManagementContext.Provider value={{
        resource_urls: selected,
        select,
        deselect,
        setSelected: (resource: Selectable, selected: boolean) => selected? select(resource) : deselect(resource),
        toggleSelected,
        isSelected,
        clearSelections: () => setSelected([])
    }}>
        {children}
    </SelectionManagementContext.Provider>
}