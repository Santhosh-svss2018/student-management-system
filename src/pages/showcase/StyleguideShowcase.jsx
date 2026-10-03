import React, { useState } from 'react';
import {
  Palette,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Layers,
  Sliders,
  Type,
  Maximize2
} from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Input from '../../components/common/Input';
import Select from '../../components/common/Select';
import Modal from '../../components/common/Modal';
import EduManageLogo from '../../assets/EduManageLogo';

export function StyleguideShowcase() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const colors = [
    { name: 'Primary Container', hex: '#2563eb', bg: 'bg-primary-container', text: 'text-white' },
    { name: 'Primary Deep', hex: '#004ac6', bg: 'bg-primary', text: 'text-white' },
    { name: 'Primary Fixed', hex: '#dbe1ff', bg: 'bg-primary-fixed', text: 'text-[#00174b]' },
    { name: 'Tertiary Container', hex: '#007d55', bg: 'bg-tertiary-container', text: 'text-white' },
    { name: 'Tertiary Fixed Dim', hex: '#4edea3', bg: 'bg-tertiary-fixed-dim', text: 'text-[#002113]' },
    { name: 'Secondary Container', hex: '#dae2fd', bg: 'bg-secondary-container', text: 'text-[#131b2e]' },
    { name: 'Surface Container Low', hex: '#f2f4f6', bg: 'bg-surface-container-low', text: 'text-on-surface' },
    { name: 'Error Container', hex: '#ffdad6', bg: 'bg-error-container', text: 'text-[#93000a]' }
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-on-surface flex items-center gap-2.5">
            <Palette className="w-6 h-6 text-primary" />
            Global UI System & Consistency Showcase
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Reference standard for tokens, components, typography scales, and responsive layout primitives.
          </p>
        </div>

        <Button variant="outline" size="sm" icon={Maximize2} onClick={() => setIsModalOpen(true)}>
          Preview Modal Dialog
        </Button>
      </div>

      {/* Brand & Identity */}
      <Card title="Brand Identity & Scalable SVG Marks">
        <div className="p-6 bg-slate-900 rounded-xl flex flex-wrap items-center justify-around gap-6">
          <EduManageLogo showText={true} textClassName="text-white" />
          <EduManageLogo showText={false} />
        </div>
      </Card>

      {/* Color Swatches */}
      <Card title="Material 3 / Modern Theme Palette">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {colors.map((c, i) => (
            <div key={i} className={`p-4 rounded-xl ${c.bg} ${c.text} shadow-xs border border-outline-variant/30 flex flex-col justify-between h-24`}>
              <span className="font-bold text-xs">{c.name}</span>
              <span className="text-[11px] opacity-90 font-mono">{c.hex}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Buttons Showcase */}
      <Card title="Button Component Hierarchy & States">
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="container">Primary Container</Button>
          <Button variant="primary">Primary Solid</Button>
          <Button variant="secondary">Secondary Soft</Button>
          <Button variant="outline">Outline Standard</Button>
          <Button variant="ghost">Ghost Action</Button>
          <Button variant="danger">Danger Action</Button>
          <Button variant="tertiaryFixed">Tertiary Fixed</Button>
          <Button variant="primary" disabled>Disabled State</Button>
        </div>
      </Card>

      {/* Badges & Tags */}
      <Card title="Badge & Indicator Variations">
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="primary">Primary Tag</Badge>
          <Badge variant="success" dot>Active Record</Badge>
          <Badge variant="warning" dot>Pending Approval</Badge>
          <Badge variant="error" dot>High Risk Alert</Badge>
          <Badge variant="info">Information</Badge>
          <Badge variant="neutral">Neutral State</Badge>
        </div>
      </Card>

      {/* Form Controls */}
      <Card title="Standard Form Primitives">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Input label="Text Input Field" placeholder="Enter standard text..." />
          <Input label="Error Validation State" defaultValue="invalid.email" error="Please enter a valid academic address" />
          <Select label="Dropdown Select" options={['Option Alpha', 'Option Beta', 'Option Gamma']} />
        </div>
      </Card>

      {/* Interactive Modal Test */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Interactive System Modal"
        subtitle="Standard accessible overlay component"
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>
              Close
            </Button>
            <Button variant="container" size="sm" onClick={() => setIsModalOpen(false)}>
              Confirm Action
            </Button>
          </>
        }
      >
        <p className="text-xs sm:text-sm text-on-surface leading-relaxed">
          This modal conforms with the Google Stitch design guidelines: backdrop blur, rounded-2xl elevation, and keyboard accessible Escape closing.
        </p>
      </Modal>
    </div>
  );
}

export default StyleguideShowcase;
